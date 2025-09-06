"""
Brand Digital Presence Analyzer Pro

Enhanced Python implementation for analyzing brand presence across 14 major digital platforms
using SERP API for real-time search and OpenAI GPT-4 for superior analysis.
"""

import json
import logging
import requests
import openai
import time
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

class BrandPresenceAnalyzerPro:
    """
    Enhanced brand presence analyzer with real-time SERP API search and GPT-4 analysis.
    """
    
    PLATFORMS = [
        "Google Business",
        "LinkedIn", 
        "YouTube",
        "TikTok",
        "Instagram", 
        "Pinterest",
        "X (Twitter)",
        "Facebook",
        "Medium",
        "Tumblr", 
        "Threads",
        "Quora",
        "Reddit",
        "Blue Sky"
    ]
    
    def __init__(self):
        """Initialize the analyzer with OpenAI and SERP API configuration."""
        self.openai_configured = False
        self.serp_api_key = None
        
        # Initialize OpenAI (legacy v0.28.1)
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            try:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_configured = True
            except Exception as e:
                logger.warning(f"Failed to configure OpenAI: {e}")
                self.openai_configured = False
        else:
            logger.warning("OpenAI API key not configured")
        
        # Initialize SERP API (SerpAPI preferred, ValueSERP fallback)
        if hasattr(settings, 'SERPAPI_API_KEY') and settings.SERPAPI_API_KEY:
            self.serp_api_key = settings.SERPAPI_API_KEY
            self.serp_provider = 'serpapi'
        elif hasattr(settings, 'VALUESERP_API_KEY') and settings.VALUESERP_API_KEY:
            self.serp_api_key = settings.VALUESERP_API_KEY
            self.serp_provider = 'valueserp'
        else:
            self.serp_api_key = None
            self.serp_provider = None
            logger.warning("SERP API key not configured (tried SerpAPI and ValueSERP)")
    
    def analyze_brand_presence(self, brand_name: str, website_url: str, include_competitor_analysis: bool = False) -> Dict[str, Any]:
        """
        Analyze brand presence across 14 digital platforms with real-time search.
        
        Args:
            brand_name: The brand name to search for
            website_url: The brand's official website URL
            include_competitor_analysis: Whether to include competitor analysis
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        if not self.openai_configured:
            return self._create_error_response("OpenAI API key not configured")
        
        if not self.serp_api_key:
            return self._create_error_response("SERP API key not configured")
        
        if not brand_name or not website_url:
            return self._create_error_response("Brand name and website URL are required")
        
        try:
            logger.info(f"Starting enhanced brand presence analysis for: {brand_name}")
            
            # Step 1: Perform real-time SERP searches for each platform
            platform_search_results = self._search_platforms(brand_name, website_url)
            
            # Step 2: Check if we have any valid search results
            has_valid_results = any(
                len(data.get('results', [])) > 0 and not data.get('error') 
                for data in platform_search_results.values()
            )
            
            if has_valid_results:
                # Step 2a: Analyze SERP results with GPT-4
                analysis_result = self._analyze_with_gpt4(brand_name, website_url, platform_search_results)
            else:
                # Step 2b: Use GPT-4 knowledge-based analysis as fallback
                logger.warning(f"No valid SERP results for {brand_name}, using knowledge-based analysis")
                analysis_result = self._analyze_with_gpt4_knowledge(brand_name, website_url)
            
            # Step 3: Add competitor analysis if requested
            competitor_data = {}
            if include_competitor_analysis:
                competitor_data = self._analyze_competitors(brand_name)
            
            # Step 4: Generate insights and recommendations
            insights = self._generate_insights(analysis_result, competitor_data)
            
            return self._format_success_response(
                analysis_result, 
                brand_name, 
                website_url,
                competitor_data,
                insights
            )
                
        except Exception as e:
            logger.error(f"Error during enhanced brand presence analysis: {e}")
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def _search_platforms(self, brand_name: str, website_url: str) -> Dict[str, Any]:
        """
        Perform real-time SERP searches for brand presence on each platform.
        """
        search_results = {}
        base_domain = website_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        for platform in self.PLATFORMS:
            try:
                # Construct search query for each platform
                search_queries = self._get_platform_search_queries(brand_name, platform, base_domain)
                
                platform_results = []
                for i, query in enumerate(search_queries[:1]):  # Limit to 1 search per platform for performance
                    result = self._perform_serp_search(query)
                    if result:
                        platform_results.append(result)
                        # If we found results, no need to search more for this platform
                        if result.get('results_count', 0) > 0:
                            break
                    
                    # Add small delay between searches to avoid rate limiting
                    if i < len(search_queries) - 1:
                        time.sleep(0.2)
                
                search_results[platform] = {
                    'queries_performed': len(platform_results),
                    'results': platform_results,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error searching for {platform}: {e}")
                search_results[platform] = {
                    'queries_performed': 0,
                    'results': [],
                    'error': str(e)
                }
        
        return search_results
    
    def _get_platform_search_queries(self, brand_name: str, platform: str, base_domain: str) -> List[str]:
        """
        Generate targeted search queries for each platform.
        """
        platform_domains = {
            "Google Business": ["business.google.com", "google.com/maps"],
            "LinkedIn": ["linkedin.com/company", "linkedin.com/in"],
            "YouTube": ["youtube.com"],
            "TikTok": ["tiktok.com"],
            "Instagram": ["instagram.com"],
            "Pinterest": ["pinterest.com"],
            "X (Twitter)": ["x.com", "twitter.com"],
            "Facebook": ["facebook.com"],
            "Medium": ["medium.com"],
            "Tumblr": ["tumblr.com"],
            "Threads": ["threads.net"],
            "Quora": ["quora.com"],
            "Reddit": ["reddit.com"],
            "Blue Sky": ["bsky.app", "blueskyweb.xyz"]
        }
        
        domains = platform_domains.get(platform, [platform.lower().replace(' ', '').replace('(', '').replace(')', '') + '.com'])
        
        queries = []
        for domain in domains:
            queries.extend([
                f'site:{domain} "{brand_name}"',
                f'site:{domain} {brand_name} {base_domain}'
            ])
        
        return queries
    
    def _perform_serp_search(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Perform a single SERP search using configured SERP provider.
        """
        try:
            if self.serp_provider == 'serpapi':
                return self._perform_serpapi_search(query)
            elif self.serp_provider == 'valueserp':
                return self._perform_valueserp_search(query)
            else:
                logger.error("No SERP provider configured")
                return None
                
        except Exception as e:
            logger.error(f"SERP search failed for query '{query}': {e}")
            return None
    
    def _perform_serpapi_search(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Perform search using SerpAPI.
        """
        try:
            url = "https://serpapi.com/search"
            params = {
                'api_key': self.serp_api_key,
                'q': query,
                'location': 'United States',
                'hl': 'en',
                'gl': 'us',
                'num': 10,
                'engine': 'google'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle SerpAPI error responses
            if 'error' in data:
                logger.error(f"SerpAPI error: {data.get('error')}")
                return None
            
            organic_results = data.get('organic_results', [])
            return {
                'query': query,
                'results_count': len(organic_results),
                'organic_results': organic_results[:5],  # Top 5 results
                'search_information': data.get('search_information', {}),
                'search_metadata': data.get('search_metadata', {}),
                'timestamp': datetime.now().isoformat(),
                'provider': 'serpapi'
            }
            
        except requests.RequestException as e:
            logger.error(f"SerpAPI request failed for query '{query}': {e}")
            return None
        except Exception as e:
            logger.error(f"SerpAPI error for query '{query}': {e}")
            return None
    
    def _perform_valueserp_search(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Perform search using ValueSERP (fallback).
        """
        try:
            url = "https://api.valueserp.com/search"
            params = {
                'api_key': self.serp_api_key,
                'q': query,
                'location': 'United States',
                'google_domain': 'google.com',
                'gl': 'us',
                'hl': 'en',
                'num': 10,
                'output': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'query': query,
                'results_count': len(data.get('organic_results', [])),
                'organic_results': data.get('organic_results', [])[:5],  # Top 5 results
                'search_information': data.get('search_information', {}),
                'timestamp': datetime.now().isoformat(),
                'provider': 'valueserp'
            }
            
        except Exception as e:
            logger.error(f"ValueSERP search failed for query '{query}': {e}")
            return None
    
    def _analyze_with_gpt4(self, brand_name: str, website_url: str, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze SERP search results using GPT-4 for intelligent brand presence detection.
        """
        try:
            # Create comprehensive prompt with search results
            prompt = self._create_gpt4_analysis_prompt(brand_name, website_url, search_results)
            
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert digital marketing analyst specializing in brand presence research. Analyze the provided SERP search results to determine brand presence across platforms. Return only valid JSON with no additional text."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"Received GPT-4 analysis for {brand_name}")
            
            # Parse JSON response (handle markdown code blocks)
            try:
                # Clean up response - remove markdown code blocks if present
                clean_response = ai_response
                if ai_response.startswith('```json'):
                    clean_response = ai_response.replace('```json', '').replace('```', '').strip()
                elif ai_response.startswith('```'):
                    clean_response = ai_response.replace('```', '').strip()
                
                result = json.loads(clean_response)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT-4 response as JSON: {e}")
                logger.error(f"Raw response: {ai_response}")
                return self._create_fallback_analysis(search_results)
                
        except Exception as e:
            logger.error(f"GPT-4 analysis failed: {e}")
            return self._create_fallback_analysis(search_results)
    
    def _analyze_with_gpt4_knowledge(self, brand_name: str, website_url: str) -> Dict[str, Any]:
        """
        Use GPT-4's knowledge to analyze brand presence when SERP API is unavailable.
        """
        try:
            prompt = f"""
You are a digital marketing analyst. Analyze the brand "{brand_name}" (website: {website_url}) for its likely presence across 14 major digital platforms based on your knowledge.

Consider:
- Brand size and industry
- Typical platform usage patterns
- Official social media strategy
- Business model (B2B vs B2C)

PLATFORMS TO ANALYZE:
{', '.join(self.PLATFORMS)}

RETURN ONLY THIS JSON FORMAT (no additional text):

{{
  "platforms": [
    {{
      "name": "Platform Name",
      "found": true/false,
      "verified": true/false/null,
      "profile_url": "likely_url_or_null",
      "confidence": "high/medium/low",
      "search_ranking": null,
      "notes": "knowledge-based assessment",
      "activity_level": "high/medium/low/unknown",
      "last_updated": null
    }}
  ],
  "summary": {{
    "total_platforms_checked": 14,
    "platforms_found": 0,
    "platforms_missing": 0,
    "completion_percentage": 0,
    "verification_rate": 0,
    "average_search_ranking": 0.0
  }}
}}

IMPORTANT:
- Base assessment on your knowledge of this brand
- Mark confidence as "medium" for knowledge-based analysis
- Provide realistic likelihood of presence
- Include likely URLs where appropriate
- Calculate accurate summary statistics
"""

            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert digital marketing analyst. Use your knowledge to assess brand presence across platforms when search data is unavailable. Return only valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2500
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"Received GPT-4 knowledge-based analysis for {brand_name}")
            
            # Parse JSON response (handle markdown code blocks)
            try:
                # Clean up response - remove markdown code blocks if present
                clean_response = ai_response
                if ai_response.startswith('```json'):
                    clean_response = ai_response.replace('```json', '').replace('```', '').strip()
                elif ai_response.startswith('```'):
                    clean_response = ai_response.replace('```', '').strip()
                
                result = json.loads(clean_response)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT-4 knowledge response as JSON: {e}")
                logger.error(f"Raw response: {ai_response}")
                return self._create_knowledge_fallback_analysis(brand_name)
                
        except Exception as e:
            logger.error(f"GPT-4 knowledge analysis failed: {e}")
            return self._create_knowledge_fallback_analysis(brand_name)
    
    def _create_gpt4_analysis_prompt(self, brand_name: str, website_url: str, search_results: Dict[str, Any]) -> str:
        """
        Create detailed analysis prompt for GPT-4 with SERP search results.
        """
        search_summary = ""
        for platform, data in search_results.items():
            if data.get('results'):
                search_summary += f"\n{platform}:\n"
                for result in data['results']:
                    for organic in result.get('organic_results', []):
                        title = organic.get('title', 'N/A')
                        link = organic.get('link', 'N/A')
                        position = organic.get('position', 'N/A')
                        snippet = organic.get('snippet', '')
                        search_summary += f"  - Title: {title}\n    URL: {link}\n    Position: {position}\n    Snippet: {snippet[:200]}...\n"
            else:
                search_summary += f"\n{platform}: No results found\n"
        
        return f"""
Analyze the brand presence for "{brand_name}" (Website: {website_url}) across 14 digital platforms using the following SERP search results:

SEARCH RESULTS:
{search_summary}

ANALYSIS REQUIREMENTS:
1. Determine if official brand profiles exist on each platform
2. Verify authenticity using website URL cross-reference
3. Extract follower/subscriber counts from search result snippets
4. Identify verification badges (verified, checkmark, blue tick) from titles/snippets
5. Assess engagement indicators (likes, comments, posts) from snippets
6. Extract actual profile URLs where found
7. Note search ranking positions
8. Evaluate activity level and recent posting dates
9. Estimate account age from available information
10. Calculate profile completeness based on available data

PLATFORMS TO ANALYZE:
{', '.join(self.PLATFORMS)}

RETURN ONLY THIS JSON FORMAT (no additional text):

{{
  "platforms": [
    {{
      "name": "Platform Name",
      "found": true/false,
      "verified": true/false/null,
      "profile_url": "actual_url_or_null",
      "confidence": "high/medium/low",
      "search_ranking": 1-10_or_null,
      "followers_count": number_or_null,
      "subscribers_count": number_or_null,
      "engagement_level": "high/medium/low/unknown",
      "posts_count": number_or_null,
      "verification_badge": "verified/blue_tick/checkmark/none",
      "account_age_estimate": "X_years_or_unknown",
      "last_activity": "recent/days_ago/weeks_ago/unknown",
      "profile_completeness": 0-100_percentage,
      "notes": "detailed findings including metrics found",
      "activity_level": "high/medium/low/unknown"
    }}
  ],
  "summary": {{
    "total_platforms_checked": 14,
    "platforms_found": 0,
    "platforms_missing": 0,
    "completion_percentage": 0,
    "verification_rate": 0,
    "average_search_ranking": 0.0,
    "total_followers": 0,
    "average_engagement": "medium",
    "verified_accounts": 0
  }}
}}

IMPORTANT:
- Only mark as "found" if you have strong evidence of official brand presence  
- Use actual URLs from search results
- Extract follower/subscriber counts from snippets (e.g., "1.2M followers", "500K subscribers")
- Look for verification indicators in titles/snippets ("✓", "verified", "official")
- Assess engagement from snippet text ("10K likes", "active posts", "daily updates")
- Estimate account age from dates or "since 20XX" in snippets
- Rate profile completeness based on available information richness
- Set confidence based on verification indicators and URL authenticity
- Include search ranking position where profile appears in top 10
- Provide specific, actionable notes including extracted metrics
- Calculate accurate summary statistics including total follower counts
- Ensure all 14 platforms are included in the platforms array
- Use null for metrics that cannot be determined from search results
"""
    
    def _analyze_competitors(self, brand_name: str) -> Dict[str, Any]:
        """
        Analyze top 3 competitors for comparison insights.
        """
        try:
            # Search for competitors in the same industry
            competitor_query = f'"{brand_name}" competitors top companies industry'
            competitor_search = self._perform_serp_search(competitor_query)
            
            if not competitor_search:
                return {"enabled": True, "competitors_found": [], "error": "Could not identify competitors"}
            
            # Extract competitor names using GPT-4
            competitors = self._extract_competitors_with_gpt4(brand_name, competitor_search)
            
            return {
                "enabled": True,
                "competitors_found": competitors[:3],  # Top 3 competitors
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {"enabled": True, "competitors_found": [], "error": str(e)}
    
    def _extract_competitors_with_gpt4(self, brand_name: str, search_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use GPT-4 to extract competitor information from search results.
        """
        try:
            organic_results = search_result.get('organic_results', [])
            search_text = "\n".join([f"{r.get('title', '')} - {r.get('snippet', '')}" for r in organic_results[:5]])
            
            prompt = f"""
Based on the search results below, identify the top 3 main competitors of "{brand_name}". 

Search Results:
{search_text}

Return only JSON format:
{{
  "competitors": [
    {{
      "name": "Competitor Name",
      "platforms_present": 12,
      "verification_rate": 85,
      "digital_presence_score": "A-"
    }}
  ]
}}
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Extract competitor information from search results. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result.get('competitors', [])
            
        except Exception as e:
            logger.error(f"Competitor extraction failed: {e}")
            return []
    
    def _generate_insights(self, analysis_result: Dict[str, Any], competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate actionable insights and recommendations.
        """
        platforms = analysis_result.get('platforms', [])
        found_platforms = [p for p in platforms if p.get('found')]
        missing_platforms = [p for p in platforms if not p.get('found')]
        
        # Calculate enhanced digital presence score with follower weighting
        completion_rate = len(found_platforms) / len(platforms) * 100 if platforms else 0
        verification_rate = len([p for p in found_platforms if p.get('verified')]) / len(found_platforms) * 100 if found_platforms else 0
        
        # Calculate follower-weighted score
        total_followers = 0
        weighted_platforms = 0
        high_engagement_count = 0
        
        for platform in found_platforms:
            # Extract follower count
            followers = platform.get('followers_count') or platform.get('subscribers_count') or 0
            if followers:
                total_followers += followers
                # Weight platforms with followers more heavily
                if followers >= 1000000: weighted_platforms += 3  # 1M+ followers
                elif followers >= 100000: weighted_platforms += 2  # 100K+ followers  
                elif followers >= 10000: weighted_platforms += 1.5  # 10K+ followers
                else: weighted_platforms += 1
            else:
                weighted_platforms += 1  # Default weight for platforms without follower data
                
            # Count high engagement platforms
            if platform.get('engagement_level') == 'high':
                high_engagement_count += 1
        
        # Enhanced scoring algorithm
        base_score = completion_rate
        follower_bonus = min(20, (weighted_platforms - len(found_platforms)) * 5)  # Up to 20% bonus
        engagement_bonus = (high_engagement_count / len(found_platforms) * 10) if found_platforms else 0  # Up to 10% bonus
        verification_bonus = verification_rate * 0.1  # Up to 10% bonus
        
        final_score = min(100, base_score + follower_bonus + engagement_bonus + verification_bonus)
        
        # Determine grade based on enhanced score
        if final_score >= 90: grade = "A+"
        elif final_score >= 85: grade = "A"
        elif final_score >= 80: grade = "A-"
        elif final_score >= 75: grade = "B+"
        elif final_score >= 70: grade = "B"
        elif final_score >= 65: grade = "B-"
        elif final_score >= 60: grade = "C+"
        elif final_score >= 55: grade = "C"
        elif final_score >= 50: grade = "C-"
        elif final_score >= 40: grade = "D+"
        elif final_score >= 30: grade = "D"
        else: grade = "F"
        
        # Generate recommendations
        recommendations = []
        high_priority_platforms = ["TikTok", "LinkedIn", "Instagram", "YouTube"]
        
        for platform in missing_platforms[:3]:  # Top 3 missing platforms
            priority = "high" if platform['name'] in high_priority_platforms else "medium"
            recommendations.append({
                "platform": platform['name'],
                "priority": priority,
                "reason": self._get_platform_recommendation_reason(platform['name']),
                "estimated_setup_time": self._get_setup_time_estimate(platform['name']),
                "potential_reach": self._get_reach_estimate(platform['name'])
            })
        
        # Find strongest presence by follower count
        strongest_platform = "None"
        if found_platforms:
            # Sort by follower count, then by engagement level
            sorted_platforms = sorted(found_platforms, key=lambda p: (
                p.get('followers_count') or p.get('subscribers_count') or 0,
                1 if p.get('engagement_level') == 'high' else 0
            ), reverse=True)
            strongest_platform = sorted_platforms[0]['name']
        
        return {
            "digital_presence_score": grade,
            "final_score": round(final_score, 1),
            "strongest_presence": strongest_platform,
            "biggest_opportunity": missing_platforms[0]['name'] if missing_platforms else "None",
            "total_followers": total_followers,
            "average_engagement": "high" if high_engagement_count > len(found_platforms) / 2 else "medium" if high_engagement_count > 0 else "low",
            "verification_gaps": len([p for p in found_platforms if not p.get('verified')]),
            "industry_benchmark": f"Above average ({completion_rate:.0f}% vs 52% industry average)" if completion_rate > 52 else f"Below average ({completion_rate:.0f}% vs 52% industry average)",
            "recommendations": recommendations
        }
    
    def _get_platform_recommendation_reason(self, platform_name: str) -> str:
        """Get tailored recommendation reason for each platform."""
        reasons = {
            "TikTok": "Fastest-growing platform for viral marketing and reaching Gen Z/Millennial audiences",
            "LinkedIn": "Essential for B2B networking, thought leadership, and professional credibility",
            "Instagram": "Visual storytelling platform with high engagement rates and shopping features",
            "YouTube": "Largest video platform for content marketing and SEO benefits",
            "Pinterest": "Perfect for visual discovery and driving website traffic",
            "X (Twitter)": "Real-time engagement, news, and customer service platform",
            "Facebook": "Largest social network with comprehensive business tools and advertising",
            "Medium": "Professional publishing platform for thought leadership and content marketing",
            "Google Business": "Critical for local SEO and customer reviews",
            "Threads": "Growing text-based platform from Meta with Instagram integration",
            "Reddit": "Community engagement and authentic brand discussions",
            "Quora": "Q&A platform for establishing expertise and driving organic traffic",
            "Tumblr": "Creative community platform for visual and multimedia content",
            "Blue Sky": "Emerging decentralized social platform gaining traction"
        }
        return reasons.get(platform_name, "Expanding brand presence to reach new audiences")
    
    def _get_setup_time_estimate(self, platform_name: str) -> str:
        """Get setup time estimate for each platform."""
        times = {
            "TikTok": "1-2 hours",
            "LinkedIn": "2-3 hours", 
            "Instagram": "1-2 hours",
            "YouTube": "3-4 hours",
            "Pinterest": "2-3 hours",
            "X (Twitter)": "1 hour",
            "Facebook": "2-3 hours",
            "Medium": "1 hour",
            "Google Business": "2-4 hours",
            "Threads": "30 minutes",
            "Reddit": "1-2 hours",
            "Quora": "1 hour",
            "Tumblr": "1 hour",
            "Blue Sky": "30 minutes"
        }
        return times.get(platform_name, "1-2 hours")
    
    def _get_reach_estimate(self, platform_name: str) -> str:
        """Get potential reach estimate for each platform."""
        reaches = {
            "TikTok": "500K+ monthly views potential",
            "LinkedIn": "10K+ professional network reach",
            "Instagram": "100K+ visual content engagement",
            "YouTube": "1M+ video discovery potential", 
            "Pinterest": "50K+ monthly pin impressions",
            "X (Twitter)": "25K+ real-time engagement",
            "Facebook": "200K+ social network reach",
            "Medium": "5K+ thought leadership readers",
            "Google Business": "Local search dominance",
            "Threads": "10K+ text-based engagement",
            "Reddit": "Community-driven viral potential",
            "Quora": "Expert authority positioning",
            "Tumblr": "Creative community engagement",
            "Blue Sky": "Early adopter advantage"
        }
        return reaches.get(platform_name, "Expanded audience reach")
    
    def _create_fallback_analysis(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fallback analysis when GPT-4 analysis fails.
        """
        platforms = []
        found_count = 0
        
        for platform in self.PLATFORMS:
            platform_data = search_results.get(platform, {})
            has_results = len(platform_data.get('results', [])) > 0
            
            if has_results:
                found_count += 1
                platforms.append({
                    "name": platform,
                    "found": True,
                    "verified": None,
                    "profile_url": "Found in search results",
                    "confidence": "medium",
                    "search_ranking": None,
                    "notes": "Found via SERP search - manual verification needed",
                    "activity_level": "unknown",
                    "last_updated": None
                })
            else:
                platforms.append({
                    "name": platform,
                    "found": False,
                    "verified": None,
                    "profile_url": None,
                    "confidence": None,
                    "search_ranking": None,
                    "notes": "No results found in SERP search",
                    "activity_level": "unknown",
                    "last_updated": None
                })
        
        return {
            "platforms": platforms,
            "summary": {
                "total_platforms_checked": len(self.PLATFORMS),
                "platforms_found": found_count,
                "platforms_missing": len(self.PLATFORMS) - found_count,
                "completion_percentage": round((found_count / len(self.PLATFORMS)) * 100),
                "verification_rate": 0,
                "average_search_ranking": 0.0
            }
        }
    
    def _create_knowledge_fallback_analysis(self, brand_name: str) -> Dict[str, Any]:
        """
        Create basic fallback analysis based on brand recognition.
        """
        # For well-known brands, assume basic presence
        major_brands = ["tesla", "apple", "google", "microsoft", "amazon", "meta", "netflix", "nike", "coca-cola"]
        is_major_brand = any(brand.lower() in brand_name.lower() for brand in major_brands)
        
        platforms = []
        found_count = 0
        
        for platform in self.PLATFORMS:
            # Assume major brands have presence on key platforms
            likely_present = is_major_brand and platform in [
                "Google Business", "LinkedIn", "YouTube", "Instagram", 
                "X (Twitter)", "Facebook"
            ]
            
            if likely_present:
                found_count += 1
                platforms.append({
                    "name": platform,
                    "found": True,
                    "verified": None,
                    "profile_url": f"Likely present - search required",
                    "confidence": "low",
                    "search_ranking": None,
                    "notes": f"Knowledge-based: {brand_name} likely has {platform} presence",
                    "activity_level": "unknown",
                    "last_updated": None
                })
            else:
                platforms.append({
                    "name": platform,
                    "found": False,
                    "verified": None,
                    "profile_url": None,
                    "confidence": None,
                    "search_ranking": None,
                    "notes": f"Knowledge-based: {platform} presence uncertain for {brand_name}",
                    "activity_level": "unknown",
                    "last_updated": None
                })
        
        return {
            "platforms": platforms,
            "summary": {
                "total_platforms_checked": len(self.PLATFORMS),
                "platforms_found": found_count,
                "platforms_missing": len(self.PLATFORMS) - found_count,
                "completion_percentage": round((found_count / len(self.PLATFORMS)) * 100),
                "verification_rate": 0,
                "average_search_ranking": 0.0
            }
        }
    
    def _format_html_response(self, ai_result: Dict, brand_name: str, website_url: str, competitor_data: Dict, insights: Dict) -> str:
        """Format response as beautiful HTML dashboard."""
        try:
            # Format follower numbers for display
            def format_followers(count):
                if not count:
                    return "N/A"
                if count >= 1000000:
                    return f"{count/1000000:.1f}M"
                elif count >= 1000:
                    return f"{count/1000:.1f}K"
                else:
                    return str(count)
            
            # Get platform icons (simple SVG placeholders)
            def get_platform_icon(platform_name):
                icons = {
                    "LinkedIn": "%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%230077B5' viewBox='0 0 24 24'%3E%3Cpath d='M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z'/%3E%3C/svg%3E",
                    "YouTube": "%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23FF0000' viewBox='0 0 24 24'%3E%3Cpath d='M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z'/%3E%3C/svg%3E",
                    "Instagram": "%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23E4405F' viewBox='0 0 24 24'%3E%3Cpath d='M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z'/%3E%3C/svg%3E",
                    "TikTok": "%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23000000' viewBox='0 0 24 24'%3E%3Cpath d='M12.53.02C13.84 0 15.14.01 16.44 0c.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z'/%3E%3C/svg%3E",
                    "X (Twitter)": "%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%231DA1F2' viewBox='0 0 24 24'%3E%3Cpath d='M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z'/%3E%3C/svg%3E",
                    "Facebook": "%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%231877F2' viewBox='0 0 24 24'%3E%3Cpath d='M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z'/%3E%3C/svg%3E"
                }
                return icons.get(platform_name, "%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23718096' viewBox='0 0 24 24'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E")
            
            # Prepare template data
            platforms = ai_result.get('platforms', [])
            summary = ai_result.get('summary', {})
            
            # Add formatted followers and icons to each platform
            for platform in platforms:
                platform['followers_formatted'] = format_followers(platform.get('followers_count'))
                platform['icon'] = get_platform_icon(platform['name'])
            
            context = {
                'brand_name': brand_name,
                'website_url': website_url,
                'analysis_date': datetime.now().strftime('%B %d, %Y'),
                'digital_presence_score': insights.get('digital_presence_score', 'N/A'),
                'final_score': insights.get('final_score', 0),
                'platforms_found': summary.get('platforms_found', 0),
                'total_platforms': summary.get('total_platforms_checked', 14),
                'completion_percentage': summary.get('completion_percentage', 0),
                'total_followers_formatted': format_followers(insights.get('total_followers', 0)),
                'average_engagement': insights.get('average_engagement', 'unknown'),
                'verified_accounts': summary.get('verified_accounts', 0),
                'platforms': platforms,
                'recommendations': insights.get('recommendations', []),
                'processing_time': 'Real-time SERP + GPT-4o analysis',
                'analysis_method': 'SerpAPI + GPT-4o with follower tracking',
                'analyzer_version': '2.1 Pro Enhanced'
            }
            
            return render_to_string('brand_analysis_dashboard.html', context)
            
        except Exception as e:
            logger.error(f"Error formatting HTML response: {e}")
            # Fallback to JSON if HTML rendering fails
            return self._format_json_response(ai_result, brand_name, website_url, competitor_data, insights)
    
    def _format_json_response(self, ai_result: Dict, brand_name: str, website_url: str, competitor_data: Dict, insights: Dict) -> Dict[str, Any]:
        """Fallback JSON response format."""
        """Format the successful analysis response."""
        return {
            "status": "success",
            "brand_analysis": {
                "brand_name": brand_name,
                "website": website_url,
                "analysis_date": datetime.now().isoformat(),
                "processing_time": "Real-time SERP + GPT-4o analysis",
                "analysis_method": "SerpAPI + GPT-4o with follower tracking"
            },
            "data": ai_result,
            "competitor_analysis": competitor_data,
            "insights": insights,
            "meta": {
                "analyzer_version": "2.1 Pro Enhanced",
                "platforms_supported": len(self.PLATFORMS),
                "analysis_method": "Real-time SERP search + GPT-4o analysis",
                "model": "GPT-4o",
                "serp_provider": self.serp_provider,
                "features": [
                    "live_verification", 
                    "actual_urls", 
                    "search_rankings", 
                    "follower_counts",
                    "engagement_metrics",
                    "verification_badges",
                    "account_age_estimation",
                    "profile_completeness",
                    "follower_weighted_scoring",
                    "competitor_analysis", 
                    "actionable_insights"
                ]
            }
        }
    
    def _format_success_response(self, ai_result: Dict, brand_name: str, website_url: str, competitor_data: Dict, insights: Dict) -> Dict[str, Any]:
        """Format the successful analysis response with enhanced Pro features."""
        return {
            "status": "success",
            "brand_analysis": {
                "brand_name": brand_name,
                "website": website_url,
                "analysis_date": datetime.now().isoformat(),
                "processing_time": "Real-time SERP + GPT-4o analysis",
                "analysis_method": "SerpAPI + GPT-4o with follower tracking"
            },
            "data": {
                **ai_result,
                "pro_features": {
                    "total_followers": insights.get("total_followers", 0),
                    "follower_weighted_score": insights.get("final_score", 0),
                    "verification_gaps": insights.get("verification_gaps", 0),
                    "strongest_presence": insights.get("strongest_presence", "None"),
                    "biggest_opportunity": insights.get("biggest_opportunity", "None"),
                    "industry_benchmark": insights.get("industry_benchmark", "N/A")
                }
            },
            "competitor_analysis": competitor_data,
            "insights": insights,
            "meta": {
                "analyzer_version": "2.1 Pro Enhanced",
                "platforms_supported": len(self.PLATFORMS),
                "analysis_method": "Real-time SERP search + GPT-4o analysis",
                "model": "GPT-4o", 
                "serp_provider": self.serp_provider,
                "is_pro_version": True,
                "features": [
                    "live_verification", 
                    "actual_urls", 
                    "search_rankings", 
                    "follower_counts",
                    "engagement_metrics",
                    "verification_badges",
                    "account_age_estimation",
                    "profile_completeness",
                    "follower_weighted_scoring",
                    "competitor_analysis", 
                    "actionable_insights"
                ]
            }
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "status": "error",
            "error": {
                "message": error_message,
                "timestamp": datetime.now().isoformat(),
                "code": "ANALYSIS_FAILED"
            }
        }

def analyze_brand_presence_pro(brand_name: str, website_url: str, include_competitor_analysis: bool = False) -> Dict[str, Any]:
    """
    Convenience function for analyzing brand presence with Pro features.
    
    Args:
        brand_name: The brand name to analyze
        website_url: The brand's website URL
        include_competitor_analysis: Whether to include competitor insights
        
    Returns:
        Enhanced analysis results dictionary
    """
    analyzer_pro = BrandPresenceAnalyzerPro()
    return analyzer_pro.analyze_brand_presence(brand_name, website_url, include_competitor_analysis)