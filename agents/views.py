"""
Agents views - Main imports and legacy compatibility.
This file now imports from focused modules for better code organization.
"""

# Import all views from specialized modules for backwards compatibility
from .api_views import (
    execute_agent,
    execution_list, 
    execution_detail
)

from .chat_views import (
    start_chat_session,
    send_chat_message,
    get_chat_history,
    end_chat_session,
    get_session_status,
    export_chat
)

from .web_views import (
    agents_marketplace,
    agent_detail_view,
    chat_agent_view
)

from .direct_access_views import (
    direct_access_handler,
    direct_access_display
)

# Import utility functions for backwards compatibility
from .utils import (
    validate_webhook_url,
    format_agent_message,
    AgentCompat
)

# All functionality is now available through focused modules
# This maintains backwards compatibility while improving code organization