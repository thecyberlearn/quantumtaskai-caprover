"""
REST API views for agent execution and management.
Handles API endpoints for executing agents, retrieving execution history, etc.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
# from django_ratelimit.decorators import ratelimit
from .models import AgentExecution
from .serializers import AgentExecutionSerializer
from .services import AgentFileService
from .utils import validate_webhook_url, format_agent_message
from .brand_presence_analyzer import analyze_brand_presence
from .brand_presence_analyzer_pro import analyze_brand_presence_pro
# Simplified version - basic validation only
import requests
import time
import uuid
import logging

logger = logging.getLogger('agents.api')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @ratelimit(key='user', rate='10/m', method='POST', block=True)
def execute_agent(request):
    """Execute an agent with provided input data"""
    try:
        # Validate and sanitize input data
        # Basic validation - simplified version
        validated_data = request.data
        agent_slug = validated_data.get('agent_slug')
        input_data = validated_data.get('input_data', {})
        
        if not agent_slug:
            return Response({'error': 'agent_slug is required'}, status=status.HTTP_400_BAD_REQUEST)
            
    except ValidationError as e:
        logger.warning(f"Input validation failed for user {request.user.id}: {str(e)}")
        return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)
    
    agent_data = AgentFileService.get_agent_by_slug(agent_slug)
    if not agent_data or not agent_data.get('is_active', True):
        return Response({'error': 'Agent not found'}, status=status.HTTP_404_NOT_FOUND)
    
    agent_price = float(agent_data['price'])
    
    # Check if user has sufficient balance (using existing wallet system)
    if hasattr(request.user, 'has_sufficient_balance') and not request.user.has_sufficient_balance(agent_price):
        return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create execution record
    execution = AgentExecution.objects.create(
        agent_slug=agent_data['slug'],
        agent_name=agent_data['name'],
        user=request.user,
        input_data=input_data,
        fee_charged=agent_price,
        status='pending'
    )
    
    try:
        # Deduct fee from user wallet (using existing wallet system)
        if hasattr(request.user, 'deduct_balance'):
            success = request.user.deduct_balance(
                agent_price, 
                f'{agent_data["name"]} - Execution {str(execution.id)[:8]}',
                agent_data['slug']
            )
            if not success:
                execution.status = 'failed'
                execution.error_message = 'Failed to deduct wallet balance'
                execution.save()
                return Response({'error': 'Failed to deduct wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Special handling for brand presence finder (Python implementation)
        if agent_data['slug'] == 'brand-digital-presence-finder':
            execution.status = 'running'
            execution.save()
            
            # Extract brand name and website URL from input data
            brand_name = input_data.get('brand_name')
            website_url = input_data.get('website_url')
            
            if not brand_name or not website_url:
                execution.status = 'failed'
                execution.error_message = 'Brand name and website URL are required'
                execution.save()
                return Response({'error': 'Brand name and website URL are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use Python-based brand presence analysis
            try:
                analysis_result = analyze_brand_presence(brand_name, website_url)
                
                if analysis_result.get('status') == 'success':
                    execution.status = 'completed'
                    execution.output_data = analysis_result
                    execution.completed_at = timezone.now()
                    execution.save()
                    
                    serializer = AgentExecutionSerializer(execution)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    execution.status = 'failed'
                    execution.error_message = analysis_result.get('error', {}).get('message', 'Analysis failed')
                    execution.completed_at = timezone.now()
                    execution.save()
                    
                    return Response({
                        'error': 'Brand presence analysis failed. Please try again later.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                logger.error(f"Brand presence analysis error: {e}")
                execution.status = 'failed'
                execution.error_message = f'Analysis error: {str(e)}'
                execution.completed_at = timezone.now()
                execution.save()
                
                return Response({
                    'error': 'Brand presence analysis failed. Please try again later.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Special handling for brand presence finder PRO (Enhanced Python implementation)
        elif agent_data['slug'] == 'brand-digital-presence-finder-pro':
            execution.status = 'running'
            execution.save()
            
            # Extract input data
            brand_name = input_data.get('brand_name')
            website_url = input_data.get('website_url')
            include_competitor_analysis = input_data.get('include_competitor_analysis', False)
            
            if not brand_name or not website_url:
                execution.status = 'failed'
                execution.error_message = 'Brand name and website URL are required'
                execution.save()
                return Response({'error': 'Brand name and website URL are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use enhanced Python-based brand presence analysis with SERP API + GPT-4
            try:
                analysis_result = analyze_brand_presence_pro(
                    brand_name, 
                    website_url, 
                    include_competitor_analysis
                )
                
                if analysis_result.get('status') == 'success':
                    execution.status = 'completed'
                    execution.output_data = analysis_result
                    execution.completed_at = timezone.now()
                    execution.save()
                    
                    serializer = AgentExecutionSerializer(execution)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    execution.status = 'failed'
                    execution.error_message = analysis_result.get('error', {}).get('message', 'Enhanced analysis failed')
                    execution.completed_at = timezone.now()
                    execution.save()
                    
                    return Response({
                        'error': 'Enhanced brand presence analysis failed. Please try again later.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                logger.error(f"Enhanced brand presence analysis error: {e}")
                execution.status = 'failed'
                execution.error_message = f'Enhanced analysis error: {str(e)}'
                execution.completed_at = timezone.now()
                execution.save()
                
                return Response({
                    'error': 'Enhanced brand presence analysis failed. Please try again later.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Regular webhook agents - validate webhook URL to prevent SSRF attacks
        try:
            validate_webhook_url(agent_data['webhook_url'])
        except ValueError as e:
            execution.status = 'failed'
            execution.error_message = f'Invalid webhook URL: {str(e)}'
            execution.save()
            return Response({'error': f'Invalid webhook URL: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call n8n webhook with proper payload format
        execution.status = 'running'
        execution.save()
        
        # Generate session ID
        session_id = f"session_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
        
        # Format message text for N8N based on agent type
        message_text = format_agent_message(agent_data['slug'], input_data)
        
        webhook_payload = {
            'sessionId': session_id,
            'message': {'text': message_text},
            'webhookUrl': agent_data['webhook_url'],
            'executionMode': 'production',
            'agentId': agent_data['slug'],
            'executionId': str(execution.id),
            'userId': str(request.user.id)
        }
        
        response = requests.post(
            agent_data['webhook_url'],
            json=webhook_payload,
            timeout=90,  # Increased timeout for complex processing
            headers={'Content-Type': 'application/json'}
        )
        
        # Store webhook response
        execution.webhook_response = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'raw': response.text}
        
        # Check if response contains N8N error indicators
        has_error = False
        if response.status_code == 200 and execution.webhook_response:
            # Check for N8N error patterns
            if isinstance(execution.webhook_response, dict):
                if 'errorMessage' in execution.webhook_response or 'error' in execution.webhook_response:
                    has_error = True
        
        if response.status_code == 200 and not has_error:
            execution.status = 'completed'
            execution.output_data = execution.webhook_response
            execution.completed_at = timezone.now()
            execution.save()
            
            serializer = AgentExecutionSerializer(execution)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            execution.status = 'failed'
            if has_error:
                error_msg = execution.webhook_response.get('errorMessage', 'Webhook execution failed')
                execution.error_message = f"N8N Error: {error_msg[:500]}"
            else:
                execution.error_message = f"Webhook returned {response.status_code}: {response.text[:500]}"
            execution.completed_at = timezone.now()
            execution.save()
            
            return Response({
                'error': 'Agent is temporarily unavailable. Please try again later.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except requests.RequestException as e:
        execution.status = 'failed'
        execution.error_message = str(e)
        execution.completed_at = timezone.now()
        execution.save()
        
        return Response({
            'error': 'Failed to execute agent',
            'execution_id': str(execution.id)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @ratelimit(key='user', rate='30/m', method='GET', block=True)
def execution_list(request):
    """List user's agent executions with optimized queries"""
    executions = AgentExecution.objects.filter(user=request.user).select_related('user').order_by('-created_at')
    
    # Add filtering by agent if specified
    agent_slug = request.GET.get('agent')
    if agent_slug:
        executions = executions.filter(agent_slug=agent_slug)
    
    # Add status filtering
    status_filter = request.GET.get('status')
    if status_filter:
        executions = executions.filter(status=status_filter)
    
    paginator = PageNumberPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(executions, request)
    serializer = AgentExecutionSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @ratelimit(key='user', rate='60/m', method='GET', block=True)
def execution_detail(request, execution_id):
    """Get detailed execution information"""
    execution = get_object_or_404(AgentExecution, id=execution_id, user=request.user)
    serializer = AgentExecutionSerializer(execution)
    return Response(serializer.data)