#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, '/home/amit/projects/quantumtaskai_django')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quantumtaskai_hub.settings')
django.setup()

from agent_base.models import BaseAgent

print("🔍 Checking agents in database:")
print("=" * 40)

agents = BaseAgent.objects.all()
if agents:
    for agent in agents:
        print(f"✅ {agent.name} ({agent.slug})")
        print(f"   Category: {agent.category}")
        print(f"   Price: {agent.price} AED")
        print(f"   Type: {agent.agent_type}")
        print(f"   Active: {agent.is_active}")
        print()
else:
    print("❌ No agents found in database")

print(f"Total agents: {agents.count()}")