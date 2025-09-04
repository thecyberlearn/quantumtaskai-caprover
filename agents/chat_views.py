"""
Chat functionality views for chat-based agents.
Handles chat sessions, message sending, session management, and chat exports.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
from .models import ChatSession, ChatMessage
from .services import AgentFileService
from .utils import validate_webhook_url, AgentCompat
from core.validators import validate_api_input, InputValidator
import requests
import time
import uuid
import logging

logger = logging.getLogger('agents.chat')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='5/m', method='POST', block=True)
def start_chat_session(request):
    """Start a new chat session"""
    try:
        # Validate and sanitize input data
        validated_data = validate_api_input(request.data)
        agent_slug = validated_data.get('agent_slug')
        
        if not agent_slug:
            return Response({'error': 'agent_slug is required'}, status=status.HTTP_400_BAD_REQUEST)
            
    except ValidationError as e:
        logger.warning(f"Input validation failed for user {request.user.id}: {str(e)}")
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)
    
    agent_data = AgentFileService.get_agent_by_slug(agent_slug)
    if not agent_data or not agent_data.get('is_active', True) or agent_data.get('agent_type') != 'chat':
        return Response({'error': 'Chat agent not found'}, status=status.HTTP_404_NOT_FOUND)
    
    agent_price = float(agent_data['price'])
    
    # Check wallet balance
    if hasattr(request.user, 'wallet_balance') and request.user.wallet_balance < agent_price:
        return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check for existing active session (using slug-based lookup)
    existing_session = ChatSession.objects.filter(
        agent_slug=agent_data['slug'],
        user=request.user,
        status='active'
    ).first()
    
    if existing_session:
        return Response({
            'session_id': existing_session.session_id,
            'message': 'Active session already exists'
        })
    
    # Create new chat session
    session_id = f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    
    from datetime import timedelta
    
    chat_session = ChatSession.objects.create(
        session_id=session_id,
        agent_slug=agent_data['slug'],
        agent_name=agent_data['name'],
        user=request.user,
        fee_charged=agent_price,
        status='active',
        expires_at=timezone.now() + timedelta(minutes=30)
    )
    
    # Deduct fee from wallet
    try:
        success = request.user.deduct_balance(
            agent_price, 
            f'{agent_data["name"]} - Chat Session {session_id}',
            agent_data['slug']
        )
        if not success:
            # Delete the created session if payment fails
            chat_session.delete()
            return Response({
                'error': 'Failed to process payment. Please check your wallet balance.'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Delete the created session if payment processing fails
        chat_session.delete()
        return Response({
            'error': 'Payment processing error. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Send welcome message
    welcome_message = f"""## Welcome to {agent_data["name"]}! 🔍

I'm here to guide you through the **5 Whys methodology** - a powerful problem-solving technique to uncover root causes.

### How It Works:
• **Ask "Why" 5 times** to drill down from symptoms to root causes
• **Systematic analysis** of Occurrence, Detection, and Prevention
• **Actionable insights** for effective solutions

### Getting Started:
Please describe the **specific problem** you'd like to analyze. Include:
- What happened?
- When did it occur?
- What are the immediate impacts?

Let's discover the root cause together! 💪"""
    
    ChatMessage.objects.create(
        session=chat_session,
        message_type='agent',
        content=welcome_message
    )
    
    return Response({
        'session_id': chat_session.session_id,
        'message': 'Chat session started successfully'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='20/m', method='POST', block=True)
def send_chat_message(request):
    """Send a message in a chat session"""
    try:
        # Validate and sanitize input
        session_id = InputValidator.sanitize_string(request.data.get('session_id', ''), max_length=100)
        message_content = InputValidator.sanitize_string(request.data.get('message', ''), max_length=2000).strip()
        
        if not session_id or not message_content:
            return Response({'error': 'session_id and message are required'}, status=status.HTTP_400_BAD_REQUEST)
            
    except ValidationError as e:
        logger.warning(f"Input validation failed for user {request.user.id}: {str(e)}")
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get chat session
    chat_session = get_object_or_404(
        ChatSession,
        session_id=session_id,
        user=request.user,
        status='active'
    )
    
    # Check if session is expired
    if chat_session.is_expired():
        chat_session.status = 'expired'
        chat_session.save()
        return Response({'error': 'Chat session has expired'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get agent data for message limit
    agent_data = AgentFileService.get_agent_by_slug(chat_session.agent_slug)
    message_limit = agent_data.get('message_limit', 50) if agent_data else 50
    
    # Check message limit (only count user messages) - optimized query
    current_user_message_count = ChatMessage.objects.filter(
        session=chat_session, 
        message_type='user'
    ).count()
    if current_user_message_count >= message_limit:
        # Auto-complete the session when message limit is reached
        chat_session.status = 'completed'
        chat_session.completed_at = timezone.now()
        chat_session.save()
        
        return Response({
            'error': f'Message limit reached ({message_limit} messages). Session completed. You can download your conversation or start a new session.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Save user message
    user_message = ChatMessage.objects.create(
        session=chat_session,
        message_type='user',
        content=message_content
    )
    
    # Prepare webhook payload
    webhook_payload = {
        "message": {
            "text": f"""User message: "{message_content}"

Provide helpful 5 Whys analysis guidance with professional formatting:

FORMATTING REQUIREMENTS:
- Use markdown headers (##, ###) for sections
- Use **bold** for key terms and emphasis
- Use bullet points (•) for lists
- Use numbered lists (1., 2., 3.) for steps
- Structure responses with clear sections
- Add relevant emojis for engagement

CONTENT GUIDELINES:
- Guide through 5 Whys methodology systematically
- Ask probing questions about Occurrence, Detection, Prevention
- Help user drill down from symptoms to root causes
- Keep responses conversational but structured
- Do not generate final reports - focus on interactive guidance
- Encourage deeper thinking with follow-up questions"""
        },
        "sessionId": session_id,
        "userId": str(request.user.id),
        "agentId": chat_session.agent_slug,
        "messageType": "chat"
    }
    
    try:
        # Get webhook URL from agent data
        webhook_url = agent_data['webhook_url'] if agent_data else None
        if not webhook_url:
            raise ValueError("Agent webhook URL not found")
            
        # Validate webhook URL
        validate_webhook_url(webhook_url)
        
        # Send to webhook
        response = requests.post(
            webhook_url,
            json=webhook_payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Try multiple possible response field names from N8N
            agent_response = None
            possible_fields = ['output', 'response', 'message', 'reply', 'result', 'text', 'content']
            
            # Handle array response first (your N8N case)
            if isinstance(response_data, list) and len(response_data) > 0:
                first_item = response_data[0]
                if isinstance(first_item, dict):
                    for field in possible_fields:
                        if field in first_item:
                            agent_response = first_item[field]
                            break
                elif isinstance(first_item, str):
                    agent_response = first_item
            
            # Handle direct object response
            elif isinstance(response_data, dict):
                for field in possible_fields:
                    if field in response_data:
                        agent_response = response_data[field]
                        break
            
            # If response_data is a string itself
            elif isinstance(response_data, str):
                agent_response = response_data
            
            # Fallback with full response data for debugging
            if agent_response is None:
                agent_response = f"N8N Response received but couldn't parse: {str(response_data)[:200]}..."
            
            # Save agent response
            agent_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='agent',
                content=str(agent_response),
                metadata={'webhook_response': response_data, 'raw_response': response.text}
            )
            
            # Update session timestamp and extend expiration
            chat_session.extend_session()
            
            return Response({
                'user_message': {
                    'id': str(user_message.id),
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.isoformat()
                },
                'agent_message': {
                    'id': str(agent_message.id),
                    'content': agent_message.content,
                    'timestamp': agent_message.timestamp.isoformat()
                }
            })
        else:
            # Webhook error
            error_message = "I'm having trouble processing your message right now. Please try again."
            agent_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='agent',
                content=error_message,
                metadata={'error': f'Webhook returned {response.status_code}'}
            )
            
            return Response({
                'user_message': {
                    'id': str(user_message.id),
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.isoformat()
                },
                'agent_message': {
                    'id': str(agent_message.id),
                    'content': agent_message.content,
                    'timestamp': agent_message.timestamp.isoformat()
                }
            }, status=status.HTTP_202_ACCEPTED)
            
    except Exception as e:
        # Handle webhook errors
        error_message = "I'm experiencing technical difficulties. Please try again later."
        agent_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='agent',
            content=error_message,
            metadata={'error': str(e)}
        )
        
        return Response({
            'user_message': {
                'id': str(user_message.id),
                'content': user_message.content,
                'timestamp': user_message.timestamp.isoformat()
            },
            'agent_message': {
                'id': str(agent_message.id),
                'content': agent_message.content,
                'timestamp': agent_message.timestamp.isoformat()
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request, session_id):
    """Get chat history for a session"""
    chat_session = get_object_or_404(
        ChatSession,
        session_id=session_id,
        user=request.user
    )
    
    messages = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
    
    message_data = []
    for message in messages:
        message_data.append({
            'id': str(message.id),
            'message_type': message.message_type,
            'content': message.content,
            'timestamp': message.timestamp.isoformat()
        })
    
    return Response({
        'session_id': session_id,
        'status': chat_session.status,
        'messages': message_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_chat_session(request):
    """End a chat session"""
    session_id = request.data.get('session_id')
    
    if not session_id:
        return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    chat_session = get_object_or_404(
        ChatSession,
        session_id=session_id,
        user=request.user,
        status='active'
    )
    
    chat_session.status = 'completed'
    chat_session.completed_at = timezone.now()
    chat_session.save()
    
    return Response({'message': 'Chat session ended successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_status(request, session_id):
    """Get real-time session status data"""
    chat_session = get_object_or_404(
        ChatSession,
        session_id=session_id,
        user=request.user
    )
    
    # Time calculations
    now = timezone.now()
    time_remaining_seconds = max(0, (chat_session.expires_at - now).total_seconds())
    time_remaining_minutes = int(time_remaining_seconds // 60)
    time_remaining_hours = time_remaining_minutes // 60
    time_remaining_minutes = time_remaining_minutes % 60
    
    if time_remaining_hours > 0:
        time_remaining_str = f"{time_remaining_hours}h {time_remaining_minutes}m"
    else:
        time_remaining_str = f"{time_remaining_minutes}m"
    
    # Time percentage (how much time is left)
    total_session_time = 30 * 60  # 30 minutes in seconds
    time_percentage = max(0, min(100, (time_remaining_seconds / total_session_time) * 100))
    
    # Get agent data for message limit
    agent_data = AgentFileService.get_agent_by_slug(chat_session.agent_slug)
    message_limit = agent_data.get('message_limit', 50) if agent_data else 50
    
    # Message calculations (only count user messages)
    message_count = ChatMessage.objects.filter(session=chat_session, message_type='user').count()
    message_percentage = min(100, (message_count / message_limit) * 100)
    
    return Response({
        'success': True,
        'session_id': session_id,
        'status': chat_session.status,
        'time_remaining_seconds': int(time_remaining_seconds),
        'time_remaining_str': time_remaining_str,
        'time_percentage': int(time_percentage),
        'message_count': message_count,
        'message_limit': message_limit,
        'message_percentage': int(message_percentage),
        'is_expired': chat_session.is_expired()
    })


@login_required
def export_chat(request, session_id):
    """Export chat session as PDF or TXT"""
    format_type = request.GET.get('format', 'pdf').lower()
    
    # Get chat session and verify ownership
    chat_session = get_object_or_404(
        ChatSession,
        session_id=session_id,
        user=request.user
    )
    
    # Get all messages for this session
    messages = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
    
    if not messages.exists():
        return HttpResponse('No messages found in this chat session.', status=404)
    
    if format_type == 'pdf':
        return export_chat_pdf(chat_session, messages)
    elif format_type == 'txt':
        return export_chat_txt(chat_session, messages)
    else:
        return HttpResponse('Invalid format. Use pdf or txt.', status=400)


def export_chat_pdf(chat_session, messages):
    """Generate PDF export of chat session"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    story.append(Paragraph(f"5 Whys Analysis - {chat_session.agent_name}", title_style))
    story.append(Spacer(1, 12))
    
    # Session info
    info_style = styles['Normal']
    story.append(Paragraph(f"<b>Session ID:</b> {chat_session.session_id}", info_style))
    story.append(Paragraph(f"<b>Date:</b> {chat_session.created_at.strftime('%B %d, %Y at %I:%M %p')}", info_style))
    story.append(Paragraph(f"<b>Agent:</b> {chat_session.agent_name}", info_style))
    story.append(Paragraph(f"<b>Total Messages:</b> {messages.count()}", info_style))
    story.append(Spacer(1, 20))
    
    # Messages
    user_style = ParagraphStyle(
        'UserMessage',
        parent=styles['Normal'],
        leftIndent=0,
        rightIndent=50,
        spaceBefore=12,
        spaceAfter=6,
        fontSize=10
    )
    
    agent_style = ParagraphStyle(
        'AgentMessage',
        parent=styles['Normal'],
        leftIndent=50,
        rightIndent=0,
        spaceBefore=12,
        spaceAfter=6,
        fontSize=10
    )
    
    for message in messages:
        timestamp = message.timestamp.strftime('%I:%M %p')
        
        if message.message_type == 'user':
            story.append(Paragraph(f"<b>You ({timestamp}):</b><br/>{message.content}", user_style))
        elif message.message_type == 'agent':
            story.append(Paragraph(f"<b>{chat_session.agent_name} ({timestamp}):</b><br/>{message.content}", agent_style))
        elif message.message_type == 'system':
            story.append(Paragraph(f"<i>System ({timestamp}): {message.content}</i>", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="5whys_chat_{chat_session.session_id}.pdf"'
    return response


def export_chat_txt(chat_session, messages):
    """Generate TXT export of chat session"""
    content = []
    content.append("=" * 60)
    content.append(f"5 Whys Analysis - {chat_session.agent_name}")
    content.append("=" * 60)
    content.append("")
    content.append(f"Session ID: {chat_session.session_id}")
    content.append(f"Date: {chat_session.created_at.strftime('%B %d, %Y at %I:%M %p')}")
    content.append(f"Agent: {chat_session.agent_name}")
    content.append(f"Total Messages: {messages.count()}")
    content.append("")
    content.append("-" * 60)
    content.append("CONVERSATION")
    content.append("-" * 60)
    content.append("")
    
    for message in messages:
        timestamp = message.timestamp.strftime('%I:%M %p')
        
        if message.message_type == 'user':
            content.append(f"You ({timestamp}):")
            content.append(message.content)
        elif message.message_type == 'agent':
            content.append(f"{chat_session.agent_name} ({timestamp}):")
            content.append(message.content)
        elif message.message_type == 'system':
            content.append(f"System ({timestamp}): {message.content}")
        
        content.append("")  # Empty line between messages
    
    content.append("-" * 60)
    content.append("End of Conversation")
    content.append("-" * 60)
    
    text_content = "\n".join(content)
    
    response = HttpResponse(text_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="5whys_chat_{chat_session.session_id}.txt"'
    return response