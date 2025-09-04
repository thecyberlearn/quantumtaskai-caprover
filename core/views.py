from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.core.mail import send_mail
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django_ratelimit import UNSAFE
from agents.services import AgentFileService
from .models import ContactSubmission
from django.db import connection
import logging
import re
import time

logger = logging.getLogger(__name__)
@ratelimit(key='ip', rate='60/m', method='GET', block=False)
def homepage_view(request):
    """Homepage view with agent system and rate limiting"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Homepage rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.warning(request, 'Too many requests. Please wait a moment before refreshing.')
    
    try:
        # Get featured agents for homepage from files
        all_agents = AgentFileService.get_active_agents()
        featured_agents = all_agents[:6]  # Get first 6 agents
        
        context = {
            'user_balance': request.user.wallet_balance if request.user.is_authenticated else 0,
            'featured_agents': featured_agents,
        }
        
        return render(request, 'core/homepage.html', context)
        
    except Exception as e:
        logger.error(f"Homepage view error: {e}")
        messages.error(request, 'Unable to load homepage. Please try again.')
        return render(request, 'core/homepage.html', {'featured_agents': [], 'user_balance': 0})
@ratelimit(key='ip', rate='60/m', method='GET', block=False)
def pricing_view(request):
    """Pricing page - redirect to marketplace"""
    # Redirect all pricing page access to the AI marketplace
    return redirect('agents:marketplace')


@ratelimit(key='ip', rate='60/m', method='GET', block=False)
def digital_branding_view(request):
    """Digital branding services page with rate limiting"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Digital branding page rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.warning(request, 'Too many requests. Please wait a moment before refreshing.')
    
    try:
        context = {
            'user_balance': request.user.wallet_balance if request.user.is_authenticated else 0,
        }
        
        return render(request, 'core/digital_branding.html', context)
        
    except Exception as e:
        logger.error(f"Digital branding view error: {e}")
        messages.error(request, 'Unable to load digital branding page. Please try again.')
        return render(request, 'core/digital_branding.html', {})


def validate_contact_input(name, email, message, company=""):
    """Validate and sanitize contact form input"""
    errors = []
    
    # Name validation
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters long")
    elif len(name) > 100:
        errors.append("Name must be less than 100 characters")
    elif not re.match(r'^[a-zA-Z\s\-\.\']+$', name):
        errors.append("Name contains invalid characters")
    
    # Email validation (Django handles basic format)
    if not email or len(email) > 254:
        errors.append("Please provide a valid email address")
    
    # Message validation
    if not message or len(message.strip()) < 10:
        errors.append("Message must be at least 10 characters long")
    elif len(message) > 1000:
        errors.append("Message must be less than 1000 characters")
    
    # Company validation (optional)
    if company and len(company) > 100:
        errors.append("Company name must be less than 100 characters")
    
    # Check for potential spam indicators
    spam_keywords = ['viagra', 'casino', 'lottery', 'winner', 'congratulations', 'million dollars']
    message_lower = message.lower()
    if any(keyword in message_lower for keyword in spam_keywords):
        errors.append("Message contains prohibited content")
    
    return errors


def send_contact_notification(submission):
    """Send notification email for new contact submission"""
    try:
        subject = f'New Contact Form Submission from {submission.name}'
        message = f'''
New contact form submission received:

Name: {submission.name}
Email: {submission.email}
Company: {submission.company or 'Not provided'}
IP Address: {submission.ip_address}
Submitted: {submission.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Message:
{submission.message}

---
This is an automated notification from Quantum Tasks AI contact form.
        '''
        
        # Send to admin email
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'abhay@quantumtaskai.com')
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )
        
        logger.info(f"Contact notification sent for submission from {submission.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send contact notification: {e}")
        return False


@ratelimit(key='ip', rate='3/m', method='POST', block=False)
def contact_form_view(request):
    """Handle contact form submission with security and rate limiting"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Contact form rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({
            'success': False, 
            'error': 'Too many contact form submissions. Please try again in a few minutes.'
        }, status=429)
    
    try:
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        company = request.POST.get('company', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validate input
        validation_errors = validate_contact_input(name, email, message, company)
        if validation_errors:
            logger.warning(f"Contact form validation failed from IP {request.META.get('REMOTE_ADDR')}: {validation_errors}")
            return JsonResponse({
                'success': False,
                'error': 'Please correct the following errors: ' + ', '.join(validation_errors)
            }, status=400)
        
        # Check for duplicate submissions (same email/IP in last hour)
        from django.utils import timezone
        from datetime import timedelta
        
        recent_submission = ContactSubmission.objects.filter(
            ip_address=request.META.get('REMOTE_ADDR'),
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).first()
        
        if recent_submission:
            logger.warning(f"Duplicate contact submission attempted from IP {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({
                'success': False,
                'error': 'You have already submitted a contact form recently. Please wait before submitting again.'
            }, status=429)
        
        # Create submission
        submission = ContactSubmission.objects.create(
            name=name,
            email=email,
            company=company,
            message=message,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]  # Truncate user agent
        )
        
        # Send notification email
        email_sent = send_contact_notification(submission)
        
        logger.info(f"Contact form submitted successfully from {email} (IP: {request.META.get('REMOTE_ADDR')})")
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your message! We will get back to you within 24 hours.',
            'email_sent': email_sent
        })
        
    except Exception as e:
        logger.error(f"Contact form processing error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to process your message at this time. Please try again later.'
        }, status=500)


@ratelimit(key='ip', rate='60/m', method='GET', block=False)
def health_check_view(request):
    """Simplified health check endpoint - no database dependency for startup"""
    start_time = time.time()
    health_data = {
        'status': 'healthy',
        'timestamp': int(time.time()),
        'version': '1.0',
        'app': 'quantum-tasks-ai',
        'checks': {}
    }
    
    # Basic application status - always healthy if we reach this point
    health_data['checks']['application'] = {
        'status': 'healthy',
        'django_ready': True,
        'server_running': True
    }
    
    # Try database connection but don't fail health check if it's down
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_data['checks']['database'] = {
                'status': 'healthy',
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }
            
        # If database is working, get agent count from files
        try:
            active_agents = AgentFileService.get_active_agents()
            agent_count = len(active_agents)
            health_data['checks']['agents'] = {
                'status': 'healthy',
                'active_count': agent_count
            }
        except Exception as e:
            health_data['checks']['agents'] = {
                'status': 'warning',
                'error': 'Could not load agents',
                'message': str(e)[:100]
            }
            
    except Exception as e:
        # Database connection failed - log it but don't fail health check
        health_data['checks']['database'] = {
            'status': 'warning',
            'error': 'Database connection failed',
            'message': str(e)[:100]
        }
        health_data['checks']['agents'] = {
            'status': 'skipped',
            'reason': 'database_unavailable'
        }
    
    # Environment check
    health_data['checks']['environment'] = {
        'status': 'healthy',
        'debug_mode': getattr(settings, 'DEBUG', True),
        'secret_key_configured': bool(getattr(settings, 'SECRET_KEY', None))
    }
    
    # Overall response time
    health_data['response_time_ms'] = round((time.time() - start_time) * 1000, 2)
    
    # Always return 200 - we're healthy if Django is running
    return JsonResponse(health_data, status=200)


def test_og_view(request):
    """Test page for debugging social media Open Graph previews."""
    return render(request, 'test_og.html')


# Simple external service wrapper configurations
EXTERNAL_PAGES = {
    'event': {
        'title': 'Event Registration',
        'description': 'Register for our upcoming event',
        'external_url': 'https://form.jotform.com/252214924850455',
        'template': 'iframe',  # iframe, landing, or redirect
    },
    'cea': {
        'title': 'CEA Registration',
        'description': 'Access CEA registration form',
        'external_url': 'https://agent.jotform.com/0198a8860b46796895f2a40367a6cea4df0c',
        'template': 'iframe',
    },
    'cea1': {
        'title': 'CEA1 Registration',
        'description': 'Access CEA1 registration form',
        'external_url': 'https://agent.jotform.com/0198b221344f78088bfc6fc6598d649db6e5',
        'template': 'iframe',
    },
    'demo-form': {
        'title': 'Product Demo Request', 
        'description': 'Schedule a personalized demo of our platform',
        'external_url': 'https://calendly.com/your-demo-link',
        'template': 'landing',
    },
    'consultation': {
        'title': 'Free Consultation',
        'external_url': 'https://www.jotform.com/consultation-form',
        'template': 'redirect',
    },
}


@ratelimit(key='ip', rate='30/m', method='GET', block=False)
def external_page_view(request, page_name):
    """
    Simple external service wrapper view.
    Just renders templates with external URLs - no database needed.
    """
    # Check rate limiting
    if getattr(request, 'limited', False):
        logger.warning(f"External page rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.warning(request, 'Too many requests. Please wait a moment.')
        return redirect('core:homepage')
    
    # Get page config
    page_config = EXTERNAL_PAGES.get(page_name)
    if not page_config:
        raise Http404("Page not found")
    
    # Choose template
    template_map = {
        'iframe': 'wrapper/iframe.html',
        'landing': 'wrapper/landing.html', 
        'redirect': 'wrapper/redirect.html',
    }
    
    template_name = template_map.get(page_config['template'], 'wrapper/iframe.html')
    
    context = {
        'page_title': page_config['title'],
        'page_description': page_config.get('description', ''),
        'external_url': page_config['external_url'],
        'user_balance': request.user.wallet_balance if request.user.is_authenticated else 0,
    }
    
    return render(request, template_name, context)
