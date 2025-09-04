# Agent Creation Guide

Modern guide for adding new agents to the Quantum Tasks AI platform using the streamlined file-based system.

## Overview

Quantum Tasks AI uses a **simple file-based agent system**:
1. Create JSON configuration file
2. Commit to git 
3. Agent appears in marketplace automatically

**Two Agent Types:**
- **Webhook Agents** - N8N integrations with dynamic forms
- **Direct Access Agents** - External forms (JotForm, etc.) with payment processing

## Current Agents (8 Total)

### Webhook Agents (4)
- **Social Ads Generator** - 6.00 AED - Social media ad creation
- **Job Posting Generator** - 10.00 AED - Professional job postings  
- **PDF Summarizer** - 8.00 AED - Document analysis and summarization
- **5 Whys Analyzer** - 15.00 AED - Interactive root cause analysis

### Direct Access Agents (4)  
- **CyberSec Career Navigator** - FREE - Career guidance
- **AI Brand Strategist** - FREE - Brand strategy consultation
- **Lean Six Sigma Expert** - FREE - Process improvement
- **SWOT Analysis Expert** - FREE - Strategic analysis

## Categories (6 Available)
Use existing categories first to avoid proliferation:

- **`analysis`** 🧠 - Problem-solving, strategic analysis
- **`career-education`** 🎓 - Career guidance, professional development  
- **`document-processing`** 📄 - PDF analysis, file processing
- **`human-resources`** 💼 - Job postings, HR automation
- **`marketing`** 📢 - Social ads, content marketing
- **`consulting`** 💼 - Business consultation, expert advice

## Creating New Agents

### Only Step: Create JSON Configuration ⚡

Add new file in `agents/configs/agents/your-agent-name.json`:

**That's it! No other files needed.**

#### Webhook Agent Example:
```json
{
  "slug": "content-optimizer",
  "name": "Content Optimizer", 
  "short_description": "AI-powered content optimization and enhancement",
  "description": "Enhance your content with AI-powered optimization suggestions, tone analysis, and improvement recommendations.",
  "category": "marketing",
  "price": 5.0,
  "agent_type": "form",
  "system_type": "webhook",
  "form_schema": {
    "fields": [
      {
        "name": "content",
        "type": "textarea",
        "label": "Content to Optimize",
        "required": true
      },
      {
        "name": "content_type", 
        "type": "select",
        "label": "Content Type",
        "required": true,
        "options": [
          {"value": "blog", "label": "Blog Post"},
          {"value": "social", "label": "Social Media"},
          {"value": "email", "label": "Email Marketing"}
        ]
      }
    ]
  },
  "webhook_url": "http://localhost:5678/webhook/content-optimizer",
  "access_url_name": "",
  "display_url_name": ""
}
```

#### Direct Access Agent Example:
```json
{
  "slug": "business-coach",
  "name": "Business Coach",
  "short_description": "Expert business coaching consultation", 
  "description": "Get professional business coaching insights and strategic guidance from experienced consultants.",
  "category": "consulting",
  "price": 0.0,
  "agent_type": "form", 
  "system_type": "direct_access",
  "form_schema": {"fields": []},
  "webhook_url": "https://form.jotform.com/your-form-id",
  "access_url_name": "agents:direct_access_handler",
  "display_url_name": "agents:direct_access_display"
}
```

### Step 2: Commit to Git (Optional for Production)
```bash
git add agents/configs/agents/your-agent-name.json
git commit -m "Add new agent: Your Agent Name 🤖 Generated with Claude Code"
git push
```

### Step 3: Done! ✅
- **Development:** Agent loads automatically (or restart: `python manage.py runserver`)
- **Production:** Railway auto-deploys and agent appears in marketplace

**No Python code, no URL routes, no templates needed!** 🎉

## JSON Configuration Reference

### Required Fields:
- `slug` - URL identifier (kebab-case)
- `name` - Display name
- `short_description` - Brief marketplace description  
- `description` - Full description
- `category` - Must match existing category
- `price` - Price in AED (0.0 for free)
- `agent_type` - Always "form"
- `system_type` - "webhook" or "direct_access"

### System-Specific Fields:

**Webhook Agents:**
- `form_schema` - Form field definitions
- `webhook_url` - N8N webhook endpoint
- `access_url_name` - Empty ""  
- `display_url_name` - Empty ""

**Direct Access Agents:**
- `form_schema` - Usually `{"fields": []}`
- `webhook_url` - External form URL
- `access_url_name` - "agents:direct_access_handler"
- `display_url_name` - "agents:direct_access_display"

## Form Field Types (Webhook Agents)

- `text` - Single-line text input
- `textarea` - Multi-line text input
- `select` - Dropdown with options array  
- `file` - File upload with drag-and-drop
- `url` - URL input with validation
- `checkbox` - Boolean checkbox

## System Architecture Benefits 🚀

### True File-Based System
- **Zero Manual Coding**: Generic handlers for both agent types automatically handle everything
- **Zero URL Configuration**: Dynamic routing based on JSON config properties  
- **Zero Templates**: Single generic template works for all direct access agents
- **Zero Database Setup**: Pure file-based loading with intelligent caching
- **Zero Error Handling**: Automatic webhook error detection and user feedback

### Agent Type Handling
- **Webhook Agents**: Automatically generate dynamic forms from `form_schema`
- **Direct Access Agents**: Automatically handle payment processing + external redirect
- **Both Types**: Work with only JSON configuration, no additional code
- **Error Handling**: Automatically detects webhook failures (OpenAI quota, N8N issues, timeouts) and shows user-friendly messages

### Development Workflow Comparison
```bash
# ❌ Old Complex Way (6+ steps)  
1. Create JSON config
2. Write Python view functions
3. Add URL routes  
4. Create HTML templates
5. Update view imports
6. Write error handling code
7. Test and debug

# ✅ New Simple Way (1 step)
1. Create JSON config
# Done! Everything else is automatic 🎉
# - Forms, routing, error handling, user feedback all automated
```

### How Both Agent Types Work Now

**Webhook Agents:**
- JSON config → Dynamic form via `agent_detail_view`
- Form submission → N8N webhook → Results display
- Automatic error detection and user feedback
- No individual Python code needed

**Direct Access Agents:**
- JSON config → Generic payment handler  
- Payment → Generic iframe display
- No individual Python code needed

## Automatic Error Handling 🛡️

The platform now includes **completely automated error handling** for all agents:

### What's Automatically Handled
- **N8N Webhook Failures**: Service down, timeouts, configuration errors
- **AI Service Limits**: OpenAI quota exceeded, rate limits, API errors  
- **Network Issues**: Connection failures, DNS problems, timeouts
- **Invalid Responses**: Malformed data, unexpected formats

### User Experience
- **Clear Error Messages**: "Agent is temporarily unavailable. Please try again later."
- **Persistent Display**: Error shown in results area (won't disappear like notifications)
- **No Technical Jargon**: Simple, friendly language instead of HTTP status codes

### Developer Benefits
- **Zero Configuration**: No error handling code needed in JSON configs
- **Automatic Detection**: System distinguishes between success and various failure types
- **Consistent UX**: All agents have identical error handling behavior
- **Debug Friendly**: Technical errors still logged to console for troubleshooting

### Examples of Handled Errors
```json
// N8N Response (OpenAI quota exceeded)
{
  "errorMessage": "You exceeded your current quota",
  "errorDetails": {"httpCode": "429"}
}
// → User sees: "Agent is temporarily unavailable. Please try again later."

// HTTP 500 from webhook
// → User sees: "Agent is temporarily unavailable. Please try again later."

// Connection timeout
// → User sees: "Agent is temporarily unavailable. Please try again later."
```

All technical details are logged for debugging, but users always see the same friendly message.

## Custom Integration (Advanced)

For agents needing custom behavior, add views to appropriate modules:

- **API endpoints:** `agents/api_views.py`
- **Chat functionality:** `agents/chat_views.py` 
- **Web interfaces:** `agents/web_views.py`
- **Direct access handlers:** `agents/direct_access_views.py`
- **Utilities:** `agents/utils.py`

Then add URL routes in `agents/urls.py` and update marketplace template if needed.

## External Services

### For Webhook Agents:
- Create N8N workflow at webhook URL
- Configure to accept JSON payload with `sessionId`, `message`, etc.

### For Direct Access Agents:
- Create external form (JotForm, Google Forms, etc.)
- Ensure form URL is publicly accessible

## Railway Deployment

**Automatic Process:**
1. ✅ Git push triggers Railway deployment
2. ✅ Agent files are processed automatically  
3. ✅ New agents appear in production marketplace
4. ✅ No manual database work required

## Quick Tips

- **Use existing categories** - Avoid creating unnecessary new categories
- **Keep descriptions clear** - Users should understand what the agent does
- **Test webhook URLs** - Ensure N8N endpoints are accessible
- **Free vs Paid** - Set price to 0.0 for free agents
- **Consistent naming** - Use kebab-case for slugs, Title Case for names

---

*Last updated: 2025-01-15*