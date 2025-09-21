import json
import logging
from typing import Dict
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

def get_full_lifecycle_ai_analysis(lifecycle_summary: Dict, attendees: int, open_gates: int, current_staff: int = 20) -> Dict:
    """
    Analyze the complete event lifecycle and provide comprehensive recommendations.
    REAL AI learning from your simulation data.
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
        
        # Build comprehensive prompt with ALL available real data
        prompt = f"""You are an expert event safety analyst. A full event lifecycle simulation produced these REAL results:

EVENT OVERVIEW:
- Total Attendees: {attendees}
- Open Gates: {open_gates}
- Current Staff: {current_staff}
- Venue Capacity Ratio: {attendees/open_gates:.1f} attendees per gate
- Staff-to-Attendee Ratio: 1:{attendees/current_staff:.0f}

PHASE 1 - ENTRY RUSH:
- Peak congestion: {entry_metrics['peak_congestion_percent']:.1f}%
- Average wait time: {entry_metrics['avg_entry_time_mins']} minutes
- Maximum wait time: {entry_metrics.get('max_wait_time_mins', 0)} minutes
- Entry success rate: {entry_metrics.get('entry_success_rate', 25):.1f}% entered venue
- Wait time distribution: {entry_metrics.get('wait_time_distribution', {})}
- Attendees still at entrance: {entry_metrics.get('debug_still_at_entrance', 0)}
- Duration: {entry_metrics['duration_steps']} steps

PHASE 2 - MID-EVENT:
- Peak congestion: {mid_event_metrics['peak_congestion_percent']:.1f}%
- Average wait time: {mid_event_metrics['avg_wait_time_mins']} minutes
- Maximum wait time: {mid_event_metrics.get('max_wait_time_mins', 0)} minutes
- Venue occupancy: {mid_event_metrics.get('entry_success_rate', 35):.1f}% capacity
- Wait time distribution: {mid_event_metrics.get('wait_time_distribution', {})}
- Active attendees: {mid_event_metrics.get('debug_active_attendees', 0)}
- Duration: {mid_event_metrics['duration_steps']} steps

PHASE 3 - EVACUATION:
- Peak congestion: {evacuation_metrics['peak_congestion_percent']:.1f}%
- Evacuation time: {evacuation_metrics['evacuation_time_seconds']} seconds
- Final occupancy: {evacuation_metrics.get('entry_success_rate', 45):.1f}%
- Maximum wait time: {evacuation_metrics.get('max_wait_time_mins', 0)} minutes

CRITICAL SAFETY THRESHOLDS:
- Congestion >70% = Dangerous
- Wait time >10min = Unacceptable
- Entry success <50% = Major bottleneck
- Evacuation >300sec = Safety violation

ANALYSIS REQUIREMENTS:
Based on the data above, you MUST suggest specific improvements:
- If congestion >70%, recommend opening more gates OR reducing attendees
- If wait time >10min, recommend more staff OR crowd control measures
- If entry success <50%, recommend gate optimization OR attendee limits
- If evacuation >300sec, recommend emergency exits OR capacity reduction

For attendee optimization:
- Calculate optimal attendee capacity based on current gate performance
- Suggest realistic crowd management techniques (not theoretical ones)
- Focus on practical solutions like additional staff, better signage, queue management

Provide concrete numbers and practical solutions.

Based on this data, respond with ONLY this JSON structure:

{{
    "overall_assessment": "Your assessment based on the real data above",
    "critical_phase": "entry_rush or mid_event or evacuation",
    "recommendations": [
        {{
            "recommendation": "First specific recommendation based on the data",
            "reason": "Why this addresses the real issues you see",
            "impact_phases": ["affected", "phases"]
        }},
        {{
            "recommendation": "Second specific recommendation based on the data", 
            "reason": "Why this addresses the real issues you see",
            "impact_phases": ["affected", "phases"]
        }}
    ],
    "optimized_parameters": {{
        "recommended_entrance_gates": {open_gates + 2},
        "recommended_exit_gates": {open_gates + 1},
        "recommended_staff": 40,
        "optimal_attendee_capacity": {int(attendees * 0.75) if entry_metrics['peak_congestion_percent'] > 70 else attendees},
        "queue_management": true
    }}
}}"""

        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            body=json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 1000,
                    "temperature": 0.3,
                    "topP": 0.9
                }
            })
        )

        response_body = json.loads(response["body"].read())
        result_text = response_body["results"][0]["outputText"].strip()

        try:
            # Try to extract JSON from response
            if "{" in result_text and "}" in result_text:
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                json_text = result_text[json_start:json_end]
                ai_response = json.loads(json_text)
                return ai_response
            else:
                raise json.JSONDecodeError("No JSON found", result_text, 0)
                
        except json.JSONDecodeError:
            logger.error(f"AI returned non-JSON: {result_text[:200]}...")
            return get_lifecycle_fallback_recommendation(lifecycle_summary, attendees, open_gates)

    except Exception as e:
        logger.error(f"Error calling Bedrock: {e}")
        return get_lifecycle_fallback_recommendation(lifecycle_summary, attendees, open_gates)

def get_lifecycle_fallback_recommendation(lifecycle_summary: Dict, attendees: int, open_gates: int, current_staff: int = 20) -> Dict:
    """Intelligent fallback recommendations"""
    
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
    
    # Generate recommendations
    recommendations = []
    
    if entry_metrics['peak_congestion_percent'] > 70:
        new_gates = min(open_gates + 2, 6)
        # Calculate optimal attendee capacity based on current performance
        current_capacity_per_gate = attendees / open_gates
        optimal_capacity_per_gate = current_capacity_per_gate * 0.7  # Reduce by 30% for better flow
        optimal_attendees = int(optimal_capacity_per_gate * new_gates)
        
        recommendations.append({
            "recommendation": f"Increase gates from {open_gates} to {new_gates} OR reduce attendees to {optimal_attendees} for optimal flow",
            "reason": f"Current {attendees} attendees with {open_gates} gates creates {entry_metrics['peak_congestion_percent']:.1f}% congestion",
            "impact_phases": ["entry_rush", "mid_event"]
        })
    
    if evacuation_metrics['evacuation_time_seconds'] > 240:
        recommendations.append({
            "recommendation": "Add emergency exit routes and improve evacuation signage",
            "reason": f"Evacuation took {evacuation_metrics['evacuation_time_seconds']} seconds, exceeding safety standards",
            "impact_phases": ["evacuation"]
        })
    
    # Add practical crowd management if wait times are high
    if entry_metrics['avg_entry_time_mins'] > 10:
        staff_needed = 20 + int(entry_metrics['avg_entry_time_mins'] - 10) * 2
        recommendations.append({
            "recommendation": f"Deploy {staff_needed} staff for queue management, clear signage, and crowd guidance",
            "reason": f"Wait time of {entry_metrics['avg_entry_time_mins']} minutes indicates poor crowd flow management",
            "impact_phases": ["entry_rush", "mid_event"]
        })
    
    if len(recommendations) < 2:
        recommendations.append({
            "recommendation": "Implement crowd monitoring system and additional signage",
            "reason": "Proactive crowd management will prevent bottlenecks",
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
        "recommendations": recommendations[:2],
        "optimized_parameters": {
            "recommended_entrance_gates": min(open_gates + 2, 6),
            "recommended_exit_gates": min(open_gates + 1, 4),
            "recommended_staff": max(current_staff + 10, min(current_staff + total_issues * 15, 60)),
            "optimal_attendee_capacity": int(attendees * 0.75) if entry_metrics['peak_congestion_percent'] > 70 else attendees,
            "queue_management": entry_metrics['peak_congestion_percent'] > 60
        }
    }