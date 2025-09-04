#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, '/home/amit/Desktop/quantum_ai')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quantumtaskai_hub.settings')
django.setup()

from agent_base.models import BaseAgent
from core.views import homepage_view
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser

def test_agent_visibility():
    print("🧪 Testing Agent System Integration")
    print("=" * 40)
    
    # Check agents in database
    agents = BaseAgent.objects.filter(is_active=True)
    print(f"✅ Active agents in database: {agents.count()}")
    
    for agent in agents:
        print(f"   📋 {agent.name} ({agent.slug})")
        print(f"      Category: {agent.category}")
        print(f"      Price: {agent.price} AED")
        print(f"      Type: {agent.agent_type}")
        print()
    
    # Test the homepage view directly
    print("🧪 Testing Homepage View")
    print("-" * 20)
    
    request = HttpRequest()
    request.method = 'GET'
    request.user = AnonymousUser()
    request.META = {'HTTP_HOST': 'testserver'}
    
    try:
        response = homepage_view(request)
        print(f"✅ Homepage view response status: {response.status_code}")
        
        # Check if the response contains weather agent
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'Weather Reporter' in content:
                print("✅ Weather Reporter found in homepage HTML")
            else:
                print("❌ Weather Reporter not found in homepage HTML")
                
            if 'Use Now' in content:
                print("✅ 'Use Now' buttons found")
            else:
                print("❌ 'Use Now' buttons not found")
        
    except Exception as e:
        print(f"❌ Error in homepage view: {e}")

def check_url_structure():
    print("\n🧪 Checking URL Structure")
    print("=" * 40)
    
    from django.urls import reverse
    
    try:
        # Test core URLs
        homepage_url = reverse('core:homepage')
        print(f"✅ Homepage URL: {homepage_url}")
        
        marketplace_url = reverse('agent_base:marketplace')
        print(f"✅ Marketplace URL: {marketplace_url}")
        
        # Test weather reporter URL
        weather_url = reverse('weather_reporter:detail')
        print(f"✅ Weather Reporter URL: {weather_url}")
        
    except Exception as e:
        print(f"❌ URL resolution error: {e}")

if __name__ == '__main__':
    test_agent_visibility()
    check_url_structure()