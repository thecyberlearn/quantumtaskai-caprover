"""
Input validation utilities for security and data integrity.
"""

import re
import bleach
from django.core.exceptions import ValidationError
from django.utils.html import escape
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger('core.security')


class InputValidator:
    """
    Comprehensive input validation for security and data integrity.
    """
    
    # Allowed HTML tags for rich text (very restrictive)
    ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    ALLOWED_ATTRIBUTES = {}
    
    # Common injection patterns
    INJECTION_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'expression\s*\(',  # CSS expressions
        r'@import',  # CSS imports
        r'vbscript:',  # VBScript
        r'data:text/html',  # Data URLs
        r'SELECT\s+.*FROM',  # Basic SQL injection
        r'UNION\s+SELECT',  # Union SQL injection
        r'DROP\s+TABLE',  # SQL DROP
        r'INSERT\s+INTO',  # SQL INSERT
        r'DELETE\s+FROM',  # SQL DELETE
        r'UPDATE\s+.*SET',  # SQL UPDATE
        r'\|\|\s*1\s*=\s*1',  # Boolean SQL injection
        r'1\s*=\s*1',  # Boolean logic
        r'<\s*iframe',  # Iframe injection
        r'<\s*object',  # Object injection
        r'<\s*embed',  # Embed injection
    ]
    
    @classmethod
    def sanitize_string(cls, value, max_length=1000, allow_html=False):
        """
        Sanitize a string input to prevent XSS and injection attacks.
        
        Args:
            value: Input string to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow safe HTML tags
        
        Returns:
            Sanitized string
        
        Raises:
            ValidationError: If input is invalid or malicious
        """
        if not isinstance(value, str):
            try:
                value = str(value)
            except:
                raise ValidationError("Invalid input type")
        
        # Length check
        if len(value) > max_length:
            raise ValidationError(f"Input too long (max {max_length} characters)")
        
        # Check for injection patterns
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential injection attempt detected: {pattern}")
                raise ValidationError("Input contains potentially malicious content")
        
        # HTML sanitization
        if allow_html:
            # Use bleach to allow only safe HTML
            value = bleach.clean(
                value, 
                tags=cls.ALLOWED_TAGS, 
                attributes=cls.ALLOWED_ATTRIBUTES,
                strip=True
            )
        else:
            # Strip all HTML and escape special characters
            value = bleach.clean(value, tags=[], strip=True)
            value = escape(value)
        
        # Remove null bytes and other control characters
        value = value.replace('\x00', '').replace('\r', '').strip()
        
        return value
    
    @classmethod
    def validate_email(cls, email):
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
        
        Returns:
            Sanitized email address
        
        Raises:
            ValidationError: If email is invalid
        """
        if not email or len(email) > 254:
            raise ValidationError("Invalid email address")
        
        # Basic email regex (RFC 5322 simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        # Check for dangerous patterns
        dangerous_patterns = ['<', '>', '"', "'", '\\', '/', '%', '&']
        for pattern in dangerous_patterns:
            if pattern in email:
                raise ValidationError("Email contains invalid characters")
        
        return email.lower().strip()
    
    @classmethod
    def validate_decimal_amount(cls, amount, min_value=0, max_value=10000):
        """
        Validate monetary amount.
        
        Args:
            amount: Amount to validate (string, int, float, or Decimal)
            min_value: Minimum allowed value
            max_value: Maximum allowed value
        
        Returns:
            Decimal value
        
        Raises:
            ValidationError: If amount is invalid
        """
        try:
            if isinstance(amount, str):
                # Remove any non-numeric characters except decimal point
                amount = re.sub(r'[^\d.]', '', amount)
            
            decimal_amount = Decimal(str(amount))
            
            # Check range
            if decimal_amount < min_value or decimal_amount > max_value:
                raise ValidationError(f"Amount must be between {min_value} and {max_value}")
            
            # Check precision (max 2 decimal places for currency)
            if decimal_amount.quantize(Decimal('0.01')) != decimal_amount:
                raise ValidationError("Amount cannot have more than 2 decimal places")
            
            return decimal_amount
            
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError("Invalid amount format")
    
    @classmethod
    def validate_agent_slug(cls, slug):
        """
        Validate agent slug format.
        
        Args:
            slug: Agent slug to validate
        
        Returns:
            Sanitized slug
        
        Raises:
            ValidationError: If slug is invalid
        """
        if not slug or len(slug) > 100:
            raise ValidationError("Invalid agent slug")
        
        # Only allow alphanumeric, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9\-_]+$', slug):
            raise ValidationError("Agent slug contains invalid characters")
        
        return slug.lower().strip()
    
    @classmethod
    def validate_json_input(cls, data, max_size=10000):
        """
        Validate JSON input data.
        
        Args:
            data: Dictionary or JSON string to validate
            max_size: Maximum size in bytes
        
        Returns:
            Sanitized dictionary
        
        Raises:
            ValidationError: If data is invalid
        """
        import json
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON format")
        
        if not isinstance(data, dict):
            raise ValidationError("Input must be a JSON object")
        
        # Check size
        json_str = json.dumps(data)
        if len(json_str.encode('utf-8')) > max_size:
            raise ValidationError(f"Input too large (max {max_size} bytes)")
        
        # Recursively sanitize all string values
        sanitized_data = {}
        for key, value in data.items():
            # Sanitize key
            clean_key = cls.sanitize_string(str(key), max_length=100)
            
            # Sanitize value
            if isinstance(value, str):
                clean_value = cls.sanitize_string(value, max_length=2000)
            elif isinstance(value, (int, float, bool)):
                clean_value = value
            elif isinstance(value, list):
                # Sanitize list items (only strings)
                clean_value = []
                for item in value[:10]:  # Limit to 10 items
                    if isinstance(item, str):
                        clean_value.append(cls.sanitize_string(item, max_length=500))
                    elif isinstance(item, (int, float, bool)):
                        clean_value.append(item)
            else:
                # Skip complex nested objects
                continue
            
            sanitized_data[clean_key] = clean_value
        
        return sanitized_data
    
    @classmethod
    def validate_file_upload(cls, uploaded_file, allowed_extensions=None, max_size=10485760):
        """
        Validate file upload.
        
        Args:
            uploaded_file: Django UploadedFile object
            allowed_extensions: List of allowed file extensions
            max_size: Maximum file size in bytes (default 10MB)
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If file is invalid
        """
        if not uploaded_file:
            raise ValidationError("No file provided")
        
        # Check file size
        if uploaded_file.size > max_size:
            raise ValidationError(f"File too large (max {max_size // 1048576}MB)")
        
        # Check file extension
        if allowed_extensions:
            import os
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in allowed_extensions:
                raise ValidationError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
        
        # Check filename for malicious patterns
        filename = cls.sanitize_string(uploaded_file.name, max_length=255)
        
        # Additional security checks could include:
        # - MIME type validation
        # - File content scanning
        # - Virus scanning
        
        return True


def validate_api_input(request_data):
    """
    Validate API request input data.
    
    Args:
        request_data: Request data dictionary
    
    Returns:
        Sanitized data dictionary
    
    Raises:
        ValidationError: If data is invalid
    """
    validator = InputValidator()
    
    # Validate common fields
    if 'agent_slug' in request_data:
        request_data['agent_slug'] = validator.validate_agent_slug(request_data['agent_slug'])
    
    if 'input_data' in request_data:
        request_data['input_data'] = validator.validate_json_input(request_data['input_data'])
    
    if 'amount' in request_data:
        request_data['amount'] = validator.validate_decimal_amount(request_data['amount'])
    
    return request_data