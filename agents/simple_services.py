"""
Simplified agent service for basic CapRover deployment
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

class SimpleAgentService:
    """Simple agent management without caching or complex features"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    AGENTS_CONFIG_DIR = BASE_DIR / 'agents' / 'configs' / 'agents'
    CATEGORIES_CONFIG_FILE = BASE_DIR / 'agents' / 'configs' / 'categories' / 'categories.json'
    
    @classmethod
    def get_all_agents(cls) -> List[Dict]:
        """Load all agent configurations from JSON files"""
        agents = []
        
        if not cls.AGENTS_CONFIG_DIR.exists():
            return agents
            
        for file_path in cls.AGENTS_CONFIG_DIR.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    agent_data = json.load(f)
                    agent_data['slug'] = file_path.stem
                    agents.append(agent_data)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading agent {file_path}: {e}")
                continue
                
        return agents
    
    @classmethod
    def get_agent(cls, slug: str) -> Optional[Dict]:
        """Get a specific agent by slug"""
        file_path = cls.AGENTS_CONFIG_DIR / f'{slug}.json'
        
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
                agent_data['slug'] = slug
                return agent_data
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    @classmethod
    def get_categories(cls) -> Dict[str, Dict]:
        """Load category configurations"""
        try:
            with open(cls.CATEGORIES_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    @classmethod
    def get_agents_by_category(cls) -> Dict[str, List[Dict]]:
        """Group agents by category"""
        agents = cls.get_all_agents()
        categories = {}
        
        for agent in agents:
            category = agent.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(agent)
            
        return categories