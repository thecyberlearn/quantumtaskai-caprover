"""
Direct access views for external form agents.
Handles payment processing and access to external forms (JotForm, Google Forms, etc.).
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import Http404
from datetime import timedelta
from .models import AgentExecution
from .services import AgentFileService
from .utils import AgentCompat




@login_required
def direct_access_handler(request, slug):
    """
    Generic handler for direct access agents (external forms like JotForm).
    Handles payment processing and grants access to external form.
    """
    agent_data = AgentFileService.get_agent_by_slug(slug)
    if not agent_data or not agent_data.get('is_active', True):
        raise Http404("Agent not found")
    
    # Convert to compatible object
    agent = AgentCompat(agent_data)
    
    # Verify this is a direct access agent
    if not agent.access_url_name or not agent.display_url_name:
        messages.error(request, 'This agent does not support direct access.')
        return redirect('agents:marketplace')
    
    agent_price = agent.price
    
    # Handle payment for paid agents
    if agent_price > 0:
        user_balance = request.user.wallet_balance
        if user_balance < agent_price:
            messages.error(request, f'Insufficient balance. You need {agent_price} AED but have {user_balance} AED.')
            return redirect('wallet:wallet')
        
        # Process payment
        try:
            from wallet.models import WalletTransaction
            WalletTransaction.objects.create(
                user=request.user,
                amount=-agent_price,
                type='agent_usage',
                description=f'Payment for {agent.name}',
                agent_slug=agent.slug
            )
        except Exception as e:
            messages.error(request, 'Payment processing failed. Please try again.')
            return redirect('agents:agent_detail', slug=slug)
    
    # Grant access - redirect directly to display page
    return redirect('agents:direct_access_display', slug=slug)


@login_required  
def direct_access_display(request, slug):
    """
    Generic display handler for direct access agents.
    Shows external form (JotForm, Google Forms, etc.) in iframe or redirects directly.
    """
    agent_data = AgentFileService.get_agent_by_slug(slug)
    if not agent_data or not agent_data.get('is_active', True):
        raise Http404("Agent not found")
    
    # Convert to compatible object
    agent = AgentCompat(agent_data)
    
    # Verify this is a direct access agent
    if not agent.access_url_name or not agent.display_url_name:
        messages.error(request, 'This agent does not support direct access.')
        return redirect('agents:marketplace')
    
    # Render generic template with iframe to external form
    context = {
        'agent': agent,
        'form_url': agent.webhook_url,
        'user_balance': request.user.wallet_balance if hasattr(request.user, 'wallet_balance') else 0
    }
    
    return render(request, 'agents/direct_access_agent.html', context)
