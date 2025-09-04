"""
Brand Digital Presence Analyzer

Python implementation for analyzing brand presence across 14 major digital platforms
using Groq for fast and cost-effective AI analysis.
"""

import json
import logging
from groq import Groq
from datetime import datetime
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class BrandPresenceAnalyzer:
    """
    Analyzes brand digital presence across major platforms using Groq AI.
    """
    
    def __init__(self):
        """Initialize the analyzer with Groq configuration."""
        self.client = None
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        else:
            logger.warning("Groq API key not configured")
    
    def analyze_brand_presence(self, brand_name: str, website_url: str) -> Dict[str, Any]:
        """
        Analyze brand presence across 14 digital platforms.
        
        Args:
            brand_name: The brand name to search for
            website_url: The brand's official website URL
            
        Returns:
            Dictionary containing analysis results in structured format
        """
        if not self.client:
            return self._create_error_response("Groq API key not configured")
        
        if not brand_name or not website_url:
            return self._create_error_response("Brand name and website URL are required")
        
        try:
            logger.info(f"Starting brand presence analysis for: {brand_name}")
            
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(brand_name, website_url)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast and current model
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a digital marketing analyst. Return only valid JSON with no additional text or formatting."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            # Extract and parse the response
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"Received AI response for {brand_name}")
            
            # Parse JSON response
            try:
                result = json.loads(ai_response)
                return self._format_success_response(result, brand_name, website_url)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.error(f"Raw response: {ai_response}")
                return self._create_error_response("Invalid response format from AI")
                
        except Exception as e:
            logger.error(f"Error during brand presence analysis: {e}")
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def _create_analysis_prompt(self, brand_name: str, website_url: str) -> str:
        """Create the detailed analysis prompt for the AI."""
        return f"""
You are a digital marketing analyst specializing in brand presence research. Analyze the given brand's presence across 14 major digital platforms.

BRAND INFORMATION:
Brand Name: {brand_name}
Website: {website_url}

PLATFORMS TO ANALYZE:
1. Google Business
2. LinkedIn (Company Pages)
3. YouTube
4. TikTok
5. Instagram
6. Pinterest
7. X (Twitter)
8. Facebook (Business Pages)
9. Medium
10. Tumblr
11. Threads
12. Quora
13. Reddit
14. Blue Sky

SEARCH METHODOLOGY:
- Search for exact brand name matches
- Try variations (official, verified, brand + industry terms)
- Cross-reference with the provided website URL
- Look for verification badges and official indicators
- Assess account activity and authenticity

RETURN ONLY THIS JSON FORMAT (no additional text):

{{
  "platforms": [
    {{
      "name": "Google Business",
      "found": true,
      "verified": true,
      "profile_url": "https://example.com/profile",
      "confidence": "high",
      "notes": "Verified business listing with reviews"
    }},
    {{
      "name": "LinkedIn",
      "found": false,
      "verified": null,
      "profile_url": null,
      "confidence": null,
      "notes": "No official company page found"
    }}
  ],
  "summary": {{
    "total_platforms_checked": 14,
    "platforms_found": 8,
    "platforms_missing": 6,
    "completion_percentage": 57
  }},
  "recommendations": [
    {{
      "platform": "LinkedIn",
      "priority": "high",
      "reason": "Essential for B2B networking and credibility"
    }}
  ]
}}

IMPORTANT:
- Return ONLY valid JSON
- Set confidence as "high", "medium", or "low"
- Use null for missing data
- Include brief, helpful notes for each platform
- Focus on official business accounts, not personal profiles
- If unsure, mark confidence as "low" and explain in notes
- Ensure all 14 platforms are included in the platforms array
"""

    def _format_success_response(self, ai_result: Dict, brand_name: str, website_url: str) -> Dict[str, Any]:
        """Format the successful analysis response."""
        return {
            "status": "success",
            "brand_analysis": {
                "brand_name": brand_name,
                "website": website_url,
                "analysis_date": datetime.now().isoformat(),
                "processing_time": "AI-powered analysis"
            },
            "data": ai_result,
            "meta": {
                "analyzer_version": "1.0",
                "platforms_supported": 14,
                "analysis_method": "AI-powered research"
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

# Global analyzer instance
analyzer = BrandPresenceAnalyzer()

def analyze_brand_presence(brand_name: str, website_url: str) -> Dict[str, Any]:
    """
    Convenience function for analyzing brand presence.
    
    Args:
        brand_name: The brand name to analyze
        website_url: The brand's website URL
        
    Returns:
        Analysis results dictionary
    """
    return analyzer.analyze_brand_presence(brand_name, website_url)