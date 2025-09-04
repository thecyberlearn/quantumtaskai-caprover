"""
Utility functions for the agents app.
Contains webhook validation, message formatting, and other helper functions.
"""

import ipaddress
from urllib.parse import urlparse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def validate_webhook_url(url):
    """
    Validate webhook URL to prevent SSRF attacks.
    Implements strict security controls with special handling for development.
    """
    try:
        # Allow internal:// URLs for Python-based agents
        if url.startswith('internal://'):
            logger.info(f"Internal URL allowed: {url}")
            return True
            
        parsed = urlparse(url)
        
        # Only allow HTTP/HTTPS protocols (after internal check)
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Only HTTP/HTTPS URLs are allowed")
        
        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid hostname in URL")
        
        # Production security: Only HTTPS allowed
        if not settings.DEBUG and parsed.scheme != 'https':
            raise ValueError("Only HTTPS URLs allowed in production")
        
        # Block dangerous localhost access in production
        if not settings.DEBUG:
            # Block ALL localhost/internal access in production
            localhost_patterns = [
                'localhost', '127.0.0.1', '0.0.0.0', '::1', 
                'local', 'internal', 'private'
            ]
            if any(pattern in hostname.lower() for pattern in localhost_patterns):
                raise ValueError("Localhost/internal addresses not allowed in production")
        
        # Development mode: Allow specific localhost ports for N8N
        if settings.DEBUG and hostname in ['localhost', '127.0.0.1']:
            allowed_dev_ports = [5678, 8000, 8080, 3000]  # Common development ports
            if parsed.port in allowed_dev_ports:
                logger.info(f"Development mode: Allowing localhost URL {url}")
                return True
        
        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            
            # Block all private/internal IPs in production
            if not settings.DEBUG:
                if (ip.is_private or ip.is_loopback or ip.is_reserved or 
                    ip.is_link_local or ip.is_multicast or ip.is_unspecified):
                    raise ValueError("Internal/private IP addresses not allowed in production")
            
            # In development, only allow specific ranges
            elif settings.DEBUG:
                if ip.is_loopback:
                    # Allow loopback only for specific ports
                    allowed_dev_ports = [5678, 8000, 8080, 3000]
                    if parsed.port not in allowed_dev_ports:
                        raise ValueError(f"Loopback IP only allowed on ports {allowed_dev_ports}")
                elif (ip.is_private or ip.is_reserved or ip.is_link_local or 
                      ip.is_multicast or ip.is_unspecified):
                    raise ValueError("Internal/private IP addresses not allowed")
                    
        except ValueError as e:
            if "does not appear to be an IPv4 or IPv6 address" not in str(e):
                raise  # Re-raise if it's not just a "not an IP" error
            # If it's not an IP, it's a domain name - continue validation
        
        # Additional domain validation for production
        if not settings.DEBUG:
            # Block suspicious domain patterns
            suspicious_patterns = [
                '.local', '.internal', '.private', '.corp', '.lan',
                'metadata', 'instance-data', 'user-data'
            ]
            if any(pattern in hostname.lower() for pattern in suspicious_patterns):
                raise ValueError(f"Suspicious domain pattern detected: {hostname}")
        
        # Log successful validation
        logger.info(f"Webhook URL validated successfully: {url}")
        return True
        
    except Exception as e:
        logger.warning(f"Webhook URL validation failed for {url}: {str(e)}")
        raise ValueError(f"Invalid webhook URL: {str(e)}")


def format_agent_message(agent_slug, input_data):
    """Format input data into a message for N8N webhook based on agent type"""
    if agent_slug == 'social-ads-generator':
        description = input_data.get('description', '')
        platform = input_data.get('social_platform', '')
        emoji = input_data.get('include_emoji', 'yes')
        language = input_data.get('language', 'English')
        
        return f"Execute Social Media Ad Creator with the following parameters:. Describe what you'd like to generate: {description}. Include Emoji: {emoji.title()}. For Social Media Platform: {platform.title()}. Language: {language}."
    
    elif agent_slug == 'job-posting-generator':
        job_title = input_data.get('job_title', '')
        company_name = input_data.get('company_name', '')
        description = input_data.get('job_description', '')
        seniority = input_data.get('seniority_level', '')
        contract = input_data.get('contract_type', '')
        location = input_data.get('location', '')
        language = input_data.get('language', 'English')
        
        return f"Create a professional job posting for: {job_title} at {company_name}. Description: {description}. Seniority: {seniority}. Contract: {contract}. Location: {location}. Language: {language}. Make it comprehensive and attractive to candidates."
    
    # Default formatting for other agents
    params = [f"{key}: {value}" for key, value in input_data.items() if value]
    return f"Execute {agent_slug.replace('-', ' ').title()} with parameters: {'. '.join(params)}."


class AgentCompat:
    """
    Compatibility class to convert file-based agent data to object format
    for templates and views that expect object attributes.
    """
    def __init__(self, data):
        self.slug = data['slug']
        self.name = data['name']
        self.price = float(data['price'])
        self.webhook_url = data['webhook_url']
        self.access_url_name = data.get('access_url_name', '')
        self.display_url_name = data.get('display_url_name', '')
        self.id = data['slug']  # Use slug as ID for file-based agents
        self.message_limit = data.get('message_limit', 50)