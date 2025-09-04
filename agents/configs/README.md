# Agent Configuration System

This directory contains JSON configuration files for the Quantum Tasks AI platform's file-based agent system.

## Directory Structure

```
agents/configs/
├── categories/
│   └── categories.json          # All agent categories
├── agents/
│   ├── ai-brand-strategist.json        # Direct access agent
│   ├── cybersec-career-navigator.json  # Direct access agent  
│   ├── five-whys-analysis.json         # Chat webhook agent
│   ├── job-posting-generator.json      # Form webhook agent
│   ├── lean-six-sigma-expert.json      # Direct access agent
│   ├── pdf-summarizer.json             # File upload webhook agent
│   ├── social-ads-generator.json       # Form webhook agent
│   └── swot-analysis-expert.json       # Direct access agent
└── README.md                    # This file
```

## How It Works

**Simple File-Based System:**
1. **Categories** are defined in `categories/categories.json`
2. **Agents** are defined in individual JSON files in `agents/`
3. **File changes** are automatically loaded by the Django application
4. **Adding new agents** is as simple as creating a new JSON file

## Adding New Agents

### Step 1: Create JSON Configuration File

Create a new file in the `agents/` directory, e.g., `email-writer.json`:

```json
{
  "slug": "email-writer",
  "name": "Email Writer", 
  "short_description": "AI-powered professional email writing assistant",
  "description": "Generate professional emails for any purpose with AI assistance.",
  "category": "marketing",
  "price": 3.0,
  "agent_type": "form",
  "system_type": "webhook",
  "form_schema": {
    "fields": [
      {
        "name": "email_type",
        "type": "select",
        "label": "Email Type",
        "required": true,
        "options": [
          {"value": "business", "label": "Business Email"},
          {"value": "marketing", "label": "Marketing Email"}
        ]
      }
    ]
  },
  "webhook_url": "http://localhost:5678/webhook/email-writer",
  "access_url_name": "",
  "display_url_name": ""
}
```

### Step 2: Commit to Git

```bash
git add agents/configs/agents/email-writer.json
git commit -m "Add Email Writer agent"
git push
```

### Step 3: Agent Appears Automatically

- **Development:** Restart server to see the new agent
- **Production:** Railway auto-deploys and agent appears in marketplace

## Agent Types

### Webhook Agents (N8N Integration)
- Set `system_type`: `"webhook"`
- Include detailed `form_schema` with fields
- Set `webhook_url` to N8N endpoint
- Leave `access_url_name` and `display_url_name` empty

### Direct Access Agents (External Forms)
- Set `system_type`: `"direct_access"`
- Set `form_schema`: `{"fields": []}`
- Set `webhook_url` to external form URL (JotForm, etc.)
- Set `access_url_name`: `"agents:direct_access_handler"`
- Set `display_url_name`: `"agents:direct_access_display"`

## Current Agents (8 Total)

### Webhook Agents (4)
- **Social Ads Generator** - 6.00 AED
- **Job Posting Generator** - 10.00 AED  
- **PDF Summarizer** - 8.00 AED
- **5 Whys Analyzer** - 15.00 AED

### Direct Access Agents (4)
- **CyberSec Career Navigator** - FREE
- **AI Brand Strategist** - FREE
- **Lean Six Sigma Expert** - FREE  
- **SWOT Analysis Expert** - FREE

## Field Types for Webhook Agents

- `text`: Single-line text input
- `textarea`: Multi-line text input
- `select`: Dropdown with options array
- `file`: File upload with drag-and-drop
- `url`: URL input with validation
- `checkbox`: Boolean checkbox

## Categories (6 Available)

- **`analysis`** 🧠 - Problem-solving, strategic analysis
- **`career-education`** 🎓 - Career guidance, professional development
- **`document-processing`** 📄 - PDF analysis, file processing
- **`human-resources`** 💼 - Job postings, HR automation
- **`marketing`** 📢 - Social ads, content marketing
- **`consulting`** 💼 - Business consultation, expert advice

## Benefits

✅ **Instant Creation**: Add JSON file → agent appears automatically  
✅ **Version Controlled**: All agent definitions tracked in git  
✅ **Railway Ready**: Automatic deployment with git push  
✅ **No Database Work**: File-based system handles everything  
✅ **Scalable**: Add hundreds of agents without complexity

## Railway Deployment

**Automatic Process:**
1. ✅ Git push triggers Railway deployment
2. ✅ Agent files are processed automatically
3. ✅ New agents appear in production marketplace
4. ✅ No manual database commands required

For complete documentation, see `docs/AGENT_CREATION.md`.