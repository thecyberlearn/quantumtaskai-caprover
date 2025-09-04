import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class AgentFileService:
    """
    Service for loading agent configurations from JSON files instead of database.
    Provides caching and error handling for file-based agent management.
    """
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    AGENTS_CONFIG_DIR = BASE_DIR / 'agents' / 'configs' / 'agents'
    CATEGORIES_CONFIG_FILE = BASE_DIR / 'agents' / 'configs' / 'categories' / 'categories.json'
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached data - useful for testing and development"""
        try:
            cache.delete_many(['agent_configs_all', 'agent_categories_all'])
            logger.info("Cleared all agent cache data")
        except Exception as e:
            logger.warning(f"Could not clear cache (cache not available): {e}")
            # Cache may not be available in standalone scripts
    
    @classmethod
    def get_all_categories(cls) -> List[Dict]:
        """
        Load all agent categories from categories.json file with enhanced caching.
        Returns list of category dictionaries with caching.
        """
        cache_key = 'agent_categories_all'
        try:
            cached_categories = cache.get(cache_key)
            if cached_categories is not None:
                # In debug mode, cache for 1 minute; in production, cache for 1 hour
                return cached_categories
        except Exception:
            # Cache not available, continue with file load
            cached_categories = None
            
        try:
            if not cls.CATEGORIES_CONFIG_FILE.exists():
                logger.warning(f"Categories file not found: {cls.CATEGORIES_CONFIG_FILE}")
                return []
            
            with open(cls.CATEGORIES_CONFIG_FILE, 'r', encoding='utf-8') as f:
                categories = json.load(f)
                
            # Handle both array format and object format
            if isinstance(categories, dict) and 'categories' in categories:
                categories = categories['categories']
            elif not isinstance(categories, list):
                logger.error("Categories file should contain an array of categories")
                return []
            
            # Cache for 5 minutes in development, 1 hour in production
            try:
                cache_timeout = 300 if settings.DEBUG else 3600
                cache.set(cache_key, categories, cache_timeout)
            except Exception:
                # Cache not available, continue without caching
                pass
            
            logger.info(f"Loaded {len(categories)} categories from file")
            return categories
            
        except Exception as e:
            logger.error(f"Error loading categories: {str(e)}")
            return []
    
    @classmethod
    def get_all_agents(cls) -> List[Dict]:
        """
        Load all agent configurations from JSON files with enhanced caching.
        Returns list of agent dictionaries with caching.
        """
        cache_key = 'agent_configs_all'
        try:
            cached_agents = cache.get(cache_key)
            if cached_agents is not None:
                # Return cached data regardless of debug mode
                return cached_agents
        except Exception:
            # Cache not available, continue with file load
            cached_agents = None
            
        agents = []
        
        try:
            if not cls.AGENTS_CONFIG_DIR.exists():
                logger.warning(f"Agents config directory not found: {cls.AGENTS_CONFIG_DIR}")
                return []
            
            # Get all JSON files in the agents config directory
            json_files = list(cls.AGENTS_CONFIG_DIR.glob('*.json'))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        agent_data = json.load(f)
                    
                    # Add file-based metadata
                    agent_data['_source_file'] = str(json_file)
                    agent_data['_file_name'] = json_file.name
                    
                    # Ensure required fields exist with defaults
                    agent_data.setdefault('is_active', True)
                    agent_data.setdefault('agent_type', 'form')
                    agent_data.setdefault('system_type', 'webhook')
                    agent_data.setdefault('form_schema', {'fields': []})
                    agent_data.setdefault('access_url_name', '')
                    agent_data.setdefault('display_url_name', '')
                    
                    # Validate agent configuration
                    validation_errors = cls.validate_agent_config(agent_data)
                    if validation_errors:
                        logger.warning(f"Agent {json_file.name} has validation errors: {validation_errors}")
                        # Still include it but log the issues
                    
                    agents.append(agent_data)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in {json_file}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Error loading agent from {json_file}: {str(e)}")
                    continue
            
            # Cache for 5 minutes in development, 1 hour in production
            try:
                cache_timeout = 300 if settings.DEBUG else 3600
                cache.set(cache_key, agents, cache_timeout)
            except Exception:
                # Cache not available, continue without caching
                pass
            
            logger.info(f"Loaded {len(agents)} agents from {len(json_files)} files")
            return agents
            
        except Exception as e:
            logger.error(f"Error scanning agents directory: {str(e)}")
            return []
    
    @classmethod
    def get_agent_by_slug(cls, slug: str) -> Optional[Dict]:
        """
        Get a specific agent by its slug with category info enriched.
        Returns agent dictionary or None if not found.
        """
        agents = cls.get_all_agents()
        for agent in agents:
            if agent.get('slug') == slug:
                enriched_agents = cls._enrich_agents_with_category_info([agent])
                return enriched_agents[0] if enriched_agents else agent
        return None
    
    @classmethod
    def get_agents_by_category(cls, category_slug: str) -> List[Dict]:
        """
        Get all agents belonging to a specific category.
        Returns list of agent dictionaries with category info enriched.
        """
        agents = cls.get_all_agents()
        category_agents = [agent for agent in agents if agent.get('category') == category_slug]
        return cls._enrich_agents_with_category_info(category_agents)
    
    @classmethod
    def get_active_agents(cls) -> List[Dict]:
        """
        Get all active agents with category info enriched.
        Returns list of active agent dictionaries.
        """
        agents = cls.get_all_agents()
        active_agents = [agent for agent in agents if agent.get('is_active', True)]
        return cls._enrich_agents_with_category_info(active_agents)
    
    @classmethod
    def search_agents(cls, query: str) -> List[Dict]:
        """
        Search agents by name or description.
        Returns list of matching agent dictionaries with category info enriched.
        """
        if not query:
            return cls.get_active_agents()
        
        query_lower = query.lower()
        agents = cls.get_all_agents()
        active_agents = [agent for agent in agents if agent.get('is_active', True)]
        
        matching_agents = []
        for agent in active_agents:
            name = agent.get('name', '').lower()
            description = agent.get('description', '').lower()
            short_description = agent.get('short_description', '').lower()
            
            if (query_lower in name or 
                query_lower in description or 
                query_lower in short_description):
                matching_agents.append(agent)
        
        return cls._enrich_agents_with_category_info(matching_agents)
    
    @classmethod
    def get_category_by_slug(cls, slug: str) -> Optional[Dict]:
        """
        Get a specific category by its slug.
        Returns category dictionary or None if not found.
        """
        categories = cls.get_all_categories()
        for category in categories:
            if category.get('slug') == slug:
                return category
        return None
    
    @classmethod
    def validate_agent_config(cls, agent_data: Dict) -> List[str]:
        """
        Validate an agent configuration dictionary.
        Returns list of validation errors (empty if valid).
        """
        errors = []
        required_fields = ['slug', 'name', 'short_description', 'description', 'category', 'price']
        
        for field in required_fields:
            if field not in agent_data or agent_data[field] in [None, '']:
                errors.append(f"Missing required field: {field}")
        
        # Validate price is numeric
        try:
            float(agent_data.get('price', 0))
        except (ValueError, TypeError):
            errors.append("Price must be a valid number")
        
        # Validate category exists
        category_slug = agent_data.get('category')
        if category_slug and not cls.get_category_by_slug(category_slug):
            errors.append(f"Category '{category_slug}' does not exist")
        
        # Validate system_type
        system_type = agent_data.get('system_type', 'webhook')
        if system_type not in ['webhook', 'direct_access']:
            errors.append("system_type must be 'webhook' or 'direct_access'")
        
        return errors
    
    @classmethod
    def get_agent_stats(cls) -> Dict:
        """
        Get statistics about agents and categories.
        Returns dictionary with counts and breakdown.
        """
        agents = cls.get_all_agents()
        categories = cls.get_all_categories()
        
        active_agents = cls.get_active_agents()
        webhook_agents = [a for a in active_agents if a.get('system_type') == 'webhook']
        direct_access_agents = [a for a in active_agents if a.get('system_type') == 'direct_access']
        
        # Category breakdown (use raw agents to avoid category object issue)
        category_counts = {}
        raw_active_agents = [agent for agent in agents if agent.get('is_active', True)]
        for agent in raw_active_agents:
            category = agent.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'total_agents': len(agents),
            'active_agents': len(active_agents),
            'webhook_agents': len(webhook_agents),
            'direct_access_agents': len(direct_access_agents),
            'total_categories': len(categories),
            'category_breakdown': category_counts
        }
    
    @classmethod
    def _enrich_agents_with_category_info(cls, agents: List[Dict]) -> List[Dict]:
        """
        Enrich agent dictionaries with category information for template compatibility.
        Adds category object with icon, name, and slug for each agent.
        """
        categories = cls.get_all_categories()
        category_map = {cat['slug']: cat for cat in categories}
        
        enriched_agents = []
        for agent in agents:
            agent_copy = agent.copy()
            category_slug = agent.get('category')
            
            if category_slug and category_slug in category_map:
                # Add category object for template compatibility
                category_data = category_map[category_slug]
                agent_copy['category'] = {
                    'slug': category_data['slug'],
                    'name': category_data['name'],
                    'icon': category_data['icon'],
                    'description': category_data.get('description', '')
                }
            else:
                # Fallback category
                agent_copy['category'] = {
                    'slug': 'unknown',
                    'name': 'Unknown',
                    'icon': '❓',
                    'description': 'Unknown category'
                }
            
            enriched_agents.append(agent_copy)
        
        return enriched_agents
    
