import json
import logging
from typing import Dict
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

def get_full_lifecycle_ai_analysis(lifecycle_summary: Dict, attendees: int, open_gates: int) -> Dict:
    """
    Analyze the complete event lifecycle and provide comprehensive recommendations.
    This is the winning AI prompt that analyzes ALL THREE phases.
    """
    try:
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            config=Config(retries={"max_attempts": 3})
        )
        
        # Extract metrics from lifecycle summary
        entry_metrics = lifecycle_summary["entry_rush"]
        mid_event_metrics = lifecycle_summary["mid_event"]
        evacuation_metrics = lifecycle_summary["evacuation"]
        
        # Dynamic prompt analyzing the FULL EVENT LIFECYCLE
        prompt = f"""You are an expert event safety analyst. A full event lifecycle simulation produced the following results:

EVENT OVERVIEW:
- Total Attendees: {attendees}
- Open Gates: {open_gates}

PHASE 1 - ENTRY RUSH:
- Peak congestion reached {entry_metrics['peak_congestion_percent']:.1f}%
- Average entry time was {entry_metrics['avg_entry_time_mins']} minutes
- Duration: {entry_metrics['duration_steps']} simulation steps

PHASE 2 - MID-EVENT MINGLING:
- Peak congestion during mingling: {mid_event_metrics['peak_congestion_percent']:.1f}%
- Average wait time at facilities: {mid_event_metrics['avg_wait_time_mins']} minutes
- Duration: {mid_event_metrics['duration_steps']} simulation steps

PHASE 3 - EMERGENCY EVACUATION:
- Peak congestion during evacuation: {evacuation_metrics['peak_congestion_percent']:.1f}%
- Total evacuation time: {evacuation_metrics['evacuation_time_seconds']} seconds
- Evacuation efficiency: {"Good" if evacuation_metrics['evacuation_time_seconds'] < 300 else "Needs Improvement"}

Based on the performance across ALL THREE phases, provide the top two most impactful recommendations to improve the overall safety and efficiency of this venue layout.

Respond in valid JSON format:
{{
    "overall_assessment": "Brief overall assessment of the event",
    "critical_phase": "Which phase had the most critical issues",
    "recommendations": [
        {{
            "recommendation": "First recommendation",
            "reason": "Why this will improve the overall event",
            "impact_phases": ["list", "of", "affected", "phases"]
        }},
        {{
            "recommendation": "Second recommendation", 
            "reason": "Why this will improve the overall event",
            "impact_phases": ["list", "of", "affected", "phases"]
        }}
    ],
    "optimized_parameters": {{
        "recommended_open_gates": {open_gates + 1},
        "recommended_staff": 35,
        "staggered_entry": true,
        "additional_exits": true
    }}
}}"""

        # Claude 3 request format
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 800,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        response_body = json.loads(response["body"].read())
        result_text = response_body["content"][0]["text"].strip()

        try:
            ai_response = json.loads(result_text)
            return ai_response
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return get_lifecycle_fallback_recommendation(lifecycle_summary, attendees, open_gates)

    except Exception as e:
        logger.error(f"Error calling Bedrock: {e}")
        return get_lifecycle_fallback_recommendation(lifecycle_summary, attendees, open_gates)

def get_lifecycle_fallback_recommendation(lifecycle_summary: Dict, attendees: int, open_gates: int) -> Dict:
    """Intelligent fallback recommendations for full lifecycle analysis"""
    
    entry_metrics = lifecycle_summary["entry_rush"]
    mid_event_metrics = lifecycle_summary["mid_event"]
    evacuation_metrics = lifecycle_summary["evacuation"]
    
    # Determine critical phase
    critical_issues = []
    if entry_metrics['peak_congestion_percent'] > 80:
        critical_issues.append(("entry_rush", entry_metrics['peak_congestion_percent']))
    if mid_event_metrics['peak_congestion_percent'] > 60:
        critical_issues.append(("mid_event", mid_event_metrics['peak_congestion_percent']))
    if evacuation_metrics['evacuation_time_seconds'] > 300:
        critical_issues.append(("evacuation", evacuation_metrics['evacuation_time_seconds']))
    
    critical_phase = max(critical_issues, key=lambda x: x[1])[0] if critical_issues else "entry_rush"
    
    # Generate recommendations based on critical issues
    recommendations = []
    
    if entry_metrics['peak_congestion_percent'] > 70:
        recommendations.append({
            "recommendation": f"Increase open gates from {open_gates} to {open_gates + 2} and implement staggered entry times",
            "reason": f"Entry congestion reached {entry_metrics['peak_congestion_percent']:.1f}%, causing {entry_metrics['avg_entry_time_mins']}-minute delays",
            "impact_phases": ["entry_rush", "mid_event"]
        })
    
    if evacuation_metrics['evacuation_time_seconds'] > 240:
        recommendations.append({
            "recommendation": "Add emergency exit routes and improve evacuation signage",
            "reason": f"Evacuation took {evacuation_metrics['evacuation_time_seconds']} seconds, exceeding safety standards",
            "impact_phases": ["evacuation"]
        })
    
    if mid_event_metrics['peak_congestion_percent'] > 50:
        recommendations.append({
            "recommendation": "Redistribute food and facility locations to reduce bottlenecks",
            "reason": f"Mid-event congestion reached {mid_event_metrics['peak_congestion_percent']:.1f}% near facilities",
            "impact_phases": ["mid_event"]
        })
    
    # Ensure we have at least 2 recommendations
    if len(recommendations) < 2:
        recommendations.append({
            "recommendation": "Deploy additional staff at high-traffic areas during peak times",
            "reason": "Increased staff presence will improve crowd guidance and safety across all phases",
            "impact_phases": ["entry_rush", "mid_event", "evacuation"]
        })
    
    # Overall assessment
    total_issues = len([x for x in [entry_metrics['peak_congestion_percent'] > 70,
                                  mid_event_metrics['peak_congestion_percent'] > 50,
                                  evacuation_metrics['evacuation_time_seconds'] > 300] if x])
    
    if total_issues >= 2:
        assessment = f"Multiple critical issues detected across {total_issues} phases requiring immediate attention"
    elif total_issues == 1:
        assessment = f"One critical issue in {critical_phase} phase, otherwise manageable event flow"
    else:
        assessment = "Event flow is generally well-managed with minor optimization opportunities"
    
    return {
        "overall_assessment": assessment,
        "critical_phase": critical_phase,
        "recommendations": recommendations[:2],  # Top 2 recommendations
        "optimized_parameters": {
            "recommended_open_gates": min(open_gates + 2, 6),
            "recommended_staff": min(25 + total_issues * 10, 50),
            "staggered_entry": entry_metrics['peak_congestion_percent'] > 60,
            "additional_exits": evacuation_metrics['evacuation_time_seconds'] > 240
        }
    }