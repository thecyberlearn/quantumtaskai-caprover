# Simple Agent Creation Guide

## Quick Agent Creation

1. **Create JSON file** in `agents/configs/agents/your-agent-name.json`
2. **Add basic config**:

```json
{
  "name": "Your Agent Name",
  "description": "What your agent does",
  "category": "productivity",
  "price": 5,
  "webhook_url": "https://your-webhook-endpoint.com",
  "form_schema": {
    "fields": [
      {
        "name": "input",
        "type": "text", 
        "label": "Your Input",
        "required": true
      }
    ]
  }
}
```

3. **Restart server** - Agent appears automatically

## Available Categories

Edit `agents/configs/categories/categories.json`:
- `productivity` - Work tools
- `content` - Content creation  
- `analysis` - Data analysis
- `communication` - Communication tools

## Field Types

- `text` - Single line text
- `textarea` - Multi-line text
- `number` - Numeric input
- `email` - Email input
- `file` - File upload

That's it! Your agent will appear in the marketplace.