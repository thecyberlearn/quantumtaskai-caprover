#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, '/home/amit/projects/quantumtaskai_django')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quantumtaskai_hub.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_homepage():
    print("🧪 Testing Homepage Agent Display")
    print("=" * 40)
    
    # Create a test client
    client = Client()
    
    # Get homepage
    response = client.get('/')
    print(f"✅ Homepage response status: {response.status_code}")
    
    # Check if agents are in context
    if 'featured_agents' in response.context:
        agents = response.context['featured_agents']
        print(f"✅ Featured agents found: {agents.count()}")
        
        for agent in agents:
            print(f"   📋 {agent.name} ({agent.slug}) - {agent.price} AED")
    else:
        print("❌ No featured_agents in context")
    
    # Check if Weather Reporter is in the HTML
    html_content = response.content.decode('utf-8')
    if 'Weather Reporter' in html_content:
        print("✅ Weather Reporter found in HTML")
    else:
        print("❌ Weather Reporter not found in HTML")
    
    if 'Use Now' in html_content:
        print("✅ 'Use Now' buttons found in HTML")
    else:
        print("❌ 'Use Now' buttons not found in HTML")

def test_agent_direct_access():
    print("\n🧪 Testing Direct Agent Access")
    print("=" * 40)
    
    client = Client()
    
    # Test direct access to weather reporter
    response = client.get('/agents/weather-reporter/')
    print(f"✅ Weather Reporter direct access: {response.status_code}")
    
    if response.status_code == 200:
        html_content = response.content.decode('utf-8')
        if 'Weather Reporter Agent' in html_content:
            print("✅ Weather Reporter page loads correctly")
        else:
            print("❌ Weather Reporter page content issue")
    elif response.status_code == 302:
        print(f"✅ Redirected to: {response.url}")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")

if __name__ == '__main__':
    test_homepage()
    test_agent_direct_access()