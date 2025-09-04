from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django_ratelimit.decorators import ratelimit
from django_ratelimit import UNSAFE
from django_ratelimit.exceptions import Ratelimited
from .models import User, PasswordResetToken
import logging

logger = logging.getLogger(__name__)


def validate_password_strength(password):
    """Validate password strength on backend"""
    # Check all requirements
    has_length = len(password) >= 8
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    # Check for common weak passwords
    common_passwords = ['password', '12345678', 'qwerty', 'abc123', 'password123', '123456789']
    is_common = password.lower() in common_passwords
    
    if not (has_length and has_lower and has_upper and has_digit and has_special) or is_common:
        return ["Password must have 8+ characters, uppercase, lowercase, number, and special character"]
    
    return []




def handle_ratelimited(request, exception):
    """Custom handler for rate limited requests"""
    logger.warning(f"Rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
    messages.error(request, 'Too many attempts. Please try again in a few minutes.')
    return render(request, 'authentication/login.html')


@ratelimit(key='ip', rate='5/m', method=UNSAFE, block=False)
def login_view(request):
    """User login view with rate limiting (5 attempts per minute per IP)"""
    # Handle post-login session messages
    if 'post_login_message' in request.session:
        messages.info(request, request.session.pop('post_login_message'))
    
    # Check if rate limited
    if getattr(request, 'limited', False):
        # Use session to avoid repeated rate limit messages
        if not request.session.get('rate_limit_shown'):
            logger.warning(f"Login rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
            messages.error(request, 'Too many login attempts. Please wait before trying again.')
            request.session['rate_limit_shown'] = True
        return render(request, 'authentication/login.html')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            
            login(request, user)
            # Clear rate limit flag on successful login
            request.session.pop('rate_limit_shown', None)
            # Redirect to 'next' parameter if provided, otherwise homepage
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:homepage')
        else:
            messages.error(request, 'Invalid email or password')
            # Clear rate limit flag on any POST attempt (failed login)
            request.session.pop('rate_limit_shown', None)
    
    return render(request, 'authentication/login.html')


@ratelimit(key='ip', rate='3/m', method=UNSAFE, block=False)
def register_view(request):
    """User registration view with rate limiting (3 attempts per minute per IP)"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Registration rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.error(request, 'Too many registration attempts. Please try again in a few minutes.')
        return render(request, 'authentication/register.html')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/register.html')
        
        # Validate password strength
        password_errors = validate_password_strength(password1)
        if password_errors:
            for error in password_errors:
                messages.error(request, error)
            return render(request, 'authentication/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'authentication/register.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # Auto-login new users (no email verification required)
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('core:homepage')
        except Exception as e:
            logger.error(f"Error creating account for {email}: {str(e)}")
            messages.error(request, 'Error creating account')
    
    return render(request, 'authentication/register.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('core:homepage')


@login_required
def profile_view(request):
    """User profile view"""
    # Get all transactions first (not sliced)
    all_transactions = request.user.wallet_transactions.all()
    
    # Get recent transactions (sliced for display)
    transactions = all_transactions[:50]
    
    # Calculate usage statistics using all transactions
    total_spent = sum(abs(t.amount) for t in all_transactions if t.type == 'agent_usage')
    total_topped_up = sum(t.amount for t in all_transactions if t.type == 'top_up')
    total_agents_used = all_transactions.filter(type='agent_usage').count()
    
    # Get most used agents
    from django.db.models import Count
    popular_agents = (all_transactions.filter(type='agent_usage')
                     .values('agent_slug')
                     .annotate(count=Count('agent_slug'))
                     .order_by('-count')[:5])
    
    # Wallet status
    balance = request.user.wallet_balance
    if balance < 5:
        wallet_status = {'status': 'low', 'color': 'red', 'message': 'Low balance - Add money to continue using agents'}
    elif balance < 20:
        wallet_status = {'status': 'medium', 'color': 'orange', 'message': 'Consider adding more funds'}
    else:
        wallet_status = {'status': 'high', 'color': 'green', 'message': 'Good balance'}
    
    context = {
        'transactions': transactions,
        'total_spent': total_spent,
        'total_topped_up': total_topped_up,
        'total_agents_used': total_agents_used,
        'popular_agents': popular_agents,
        'wallet_status': wallet_status,
    }
    
    return render(request, 'authentication/profile.html', context)


@ratelimit(key='ip', rate='3/5m', method=UNSAFE, block=False)
def forgot_password_view(request):
    """Forgot password view with rate limiting (3 attempts per 5 minutes per IP)"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Password reset rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.error(request, 'Too many password reset attempts. Please try again in a few minutes.')
        return render(request, 'authentication/forgot_password.html')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Create password reset token
            reset_token = PasswordResetToken.objects.create(user=user)
            
            # Build reset URL using correct site URL
            reset_path = reverse('authentication:reset_password', kwargs={'token': reset_token.token})
            reset_url = f"{settings.SITE_URL}{reset_path}"
            
            # Send email
            subject = 'Password Reset Request'
            message = f'''
Hello {user.username},

You requested a password reset for your Quantum Tasks AI account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this reset, please ignore this email.

Best regards,
Quantum Tasks AI Team
            '''
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'If an account with that email exists, password reset instructions have been sent.')
                
                # Log successful email for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Password reset email sent successfully to {email}")
                
            except Exception as e:
                # Log the actual error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send password reset email to {email}: {str(e)}")
                
                messages.error(request, 'Unable to send reset email at this time. Please try again later.')
                
        except User.DoesNotExist:
            # Log the attempt for security monitoring but show generic message
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Password reset attempted for non-existent email: {email}")
            # Show same success message to prevent user enumeration
            messages.success(request, 'If an account with that email exists, password reset instructions have been sent.')
    
    return render(request, 'authentication/forgot_password.html')


@ratelimit(key='ip', rate='3/5m', method=UNSAFE, block=True)
def reset_password_view(request, token):
    """Reset password view with rate limiting (3 attempts per 5 minutes per IP)"""
    reset_token = get_object_or_404(PasswordResetToken, token=token)
    
    if not reset_token.is_valid():
        messages.error(request, 'This password reset link has expired or is invalid.')
        return redirect('authentication:forgot_password')
    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/reset_password.html', {'token': token})
        
        # Validate password strength
        password_errors = validate_password_strength(password1)
        if password_errors:
            for error in password_errors:
                messages.error(request, error)
            return render(request, 'authentication/reset_password.html', {'token': token})
        
        # Reset password
        user = reset_token.user
        user.set_password(password1)
        user.save()
        
        # Mark token as used
        reset_token.mark_as_used()
        
        messages.success(request, 'Password reset. You can now log in.')
        return redirect('authentication:login')
    
    return render(request, 'authentication/reset_password.html', {'token': token})




