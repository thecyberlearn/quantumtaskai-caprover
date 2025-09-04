"""
Web interface views for the agents app.
Handles template rendering for marketplace, agent detail pages, and chat interfaces.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import AgentFileService
from .models import ChatSession, ChatMessage
from .utils import AgentCompat
import time


def agents_marketplace(request):
    """Agent marketplace view"""
    # Get agents from file service
    agents = AgentFileService.get_active_agents()
    categories = AgentFileService.get_all_categories()
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        agents = AgentFileService.get_agents_by_category(category_slug)
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        agents = AgentFileService.search_agents(search_query)
    
    context = {
        'agents': agents,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
        'timestamp': int(time.time())
    }
    
    return render(request, 'agents/marketplace.html', context)


@login_required
def agent_detail_view(request, slug):
    """Render agent detail page with dynamic form or chat interface"""
    agent = AgentFileService.get_agent_by_slug(slug)
    if not agent or not agent.get('is_active', True):
        from django.http import Http404
        raise Http404("Agent not found")
    
    # Handle chat-based agents
    if agent.get('agent_type') == 'chat':
        return chat_agent_view(request, agent)
    
    # Handle form-based agents (existing behavior)
    # Get all other active agents for quick access panel
    all_agents = [a for a in AgentFileService.get_active_agents() if a['slug'] != slug]
    
    context = {
        'agent': agent,
        'all_agents': all_agents,
        'timestamp': int(time.time())  # For cache busting
    }
    
    return render(request, 'agents/agent_detail.html', context)


def chat_agent_view(request, agent):
    """Render chat interface for chat-based agents"""
    chat_session = None
    messages = []
    
    # Convert file-based agent data to compatible object if needed
    if isinstance(agent, dict):
        agent_compat = AgentCompat(agent)
    else:
        agent_compat = agent
    
    if request.user.is_authenticated:
        # Get or create active chat session (using slug-based filter for file agents)
        chat_session = ChatSession.objects.filter(
            agent_slug=agent_compat.slug,  # Changed to slug-based lookup
            user=request.user,
            status='active'
        ).first()
        
        # Get session ID from URL parameter if resuming a session
        session_id = request.GET.get('session')
        if session_id and not chat_session:
            chat_session = ChatSession.objects.filter(
                session_id=session_id,
                agent_slug=agent_compat.slug,  # Changed to slug-based lookup
                user=request.user
            ).first()
        
        # Get messages for the session
        if chat_session:
            messages = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
    
    # Get all other active agents for quick access panel
    all_agents = [a for a in AgentFileService.get_active_agents() if a['slug'] != agent_compat.slug]
    
    # Get previous sessions for this user and agent (excluding current active session)
    previous_sessions_query = ChatSession.objects.filter(
        agent_slug=agent_compat.slug,  # Changed to slug-based lookup
        user=request.user
    ).exclude(status='active').order_by('-created_at')[:5]  # Last 5 non-active sessions
    
    # Add user message count to each session
    previous_sessions = []
    for session in previous_sessions_query:
        session.user_message_count = ChatMessage.objects.filter(
            session=session, 
            message_type='user'
        ).count()
        previous_sessions.append(session)
    
    # Calculate session indicators data
    session_data = {}
    if chat_session and messages.exists():
        from django.utils import timezone
        import math
        
        # Time calculations
        now = timezone.now()
        time_elapsed = now - chat_session.created_at
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
        
        # Message calculations (only count user messages)
        user_message_count = messages.filter(message_type='user').count()
        message_limit = agent_compat.message_limit
        message_percentage = min(100, (user_message_count / message_limit) * 100)
        
        session_data = {
            'time_remaining': time_remaining_str,
            'time_percentage': int(time_percentage),
            'message_count': user_message_count,
            'message_limit': message_limit,
            'message_percentage': int(message_percentage),
        }
    
    context = {
        'agent': agent,  # Keep original agent data for template compatibility
        'chat_session': chat_session,
        'messages': messages,
        'all_agents': all_agents,
        'previous_sessions': previous_sessions,
        'timestamp': int(time.time()),
        **session_data  # Unpack session data into context
    }
    
    return render(request, 'agents/agent_chat.html', context)