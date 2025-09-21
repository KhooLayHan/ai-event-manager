import json
import logging
from typing import Dict
import os

logger = logging.getLogger(__name__)

def get_cost_aware_ai_analysis(lifecycle_summary: Dict, attendees: int, open_gates: int, current_staff: int = 20) -> Dict:
    """
    Cost-aware AI analysis - uses AWS only if budget allows, otherwise intelligent fallback
    """
    
    # AWS enabled by default with $50 budget - REAL AI LEARNING
    aws_enabled = os.environ.get("AWS_BUDGET_ENABLED", "true").lower() == "true"
    
    if aws_enabled:
        try:
            # Call REAL AWS Bedrock AI (costs ~$0.02 per call)
            from .lifecycle_bedrock_fixed import get_full_lifecycle_ai_analysis
            logger.info("🤖 CALLING REAL AWS BEDROCK AI - Learning from your data!")
            
            result = get_full_lifecycle_ai_analysis(lifecycle_summary, attendees, open_gates, current_staff)
            
            logger.info("✅ AWS Bedrock AI responded with real analysis!")
            return result
        except Exception as e:
            logger.warning(f"AWS Bedrock failed: {e}. Using free fallback.")
            from .lifecycle_bedrock import get_lifecycle_fallback_recommendation
            return get_lifecycle_fallback_recommendation(lifecycle_summary, attendees, open_gates, current_staff)
    else:
        # Use free intelligent fallback
        logger.info("Using FREE intelligent fallback analysis")
        from .lifecycle_bedrock import get_lifecycle_fallback_recommendation
        return get_lifecycle_fallback_recommendation(lifecycle_summary, attendees, open_gates, current_staff)

def estimate_monthly_cost(calls_per_day: int) -> float:
    """Estimate monthly AWS Bedrock costs"""
    cost_per_call = 0.02  # ~$0.02 per AI recommendation
    monthly_calls = calls_per_day * 30
    return monthly_calls * cost_per_call