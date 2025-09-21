#!/usr/bin/env python3
"""
Test script to demonstrate AWS Bedrock integration with intelligent fallback
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from src.aws.lifecycle_bedrock import get_full_lifecycle_ai_analysis, get_lifecycle_fallback_recommendation

def test_aws_integration():
    """Test AWS Bedrock integration with fallback"""
    
    print("Testing AWS Bedrock Integration...")
    print("=" * 50)
    
    # Sample lifecycle data (what the simulation would produce)
    sample_lifecycle_summary = {
        "entry_rush": {
            "peak_congestion_percent": 85.2,
            "avg_entry_time_mins": 25,
            "duration_steps": 100
        },
        "mid_event": {
            "peak_congestion_percent": 45.8,
            "avg_wait_time_mins": 12,
            "duration_steps": 200
        },
        "evacuation": {
            "peak_congestion_percent": 92.1,
            "evacuation_time_seconds": 320,
            "duration_steps": 150
        }
    }
    
    attendees = 2000
    open_gates = 2
    
    print(f"Test Scenario:")
    print(f"   - Attendees: {attendees}")
    print(f"   - Open Gates: {open_gates}")
    print(f"   - Entry Congestion: {sample_lifecycle_summary['entry_rush']['peak_congestion_percent']}%")
    print(f"   - Entry Wait Time: {sample_lifecycle_summary['entry_rush']['avg_entry_time_mins']} minutes")
    print(f"   - Evacuation Time: {sample_lifecycle_summary['evacuation']['evacuation_time_seconds']} seconds")
    print()
    
    # Test AWS Bedrock integration
    print("Calling AWS Bedrock for AI Analysis...")
    try:
        ai_analysis = get_full_lifecycle_ai_analysis(sample_lifecycle_summary, attendees, open_gates)
        print("AWS Bedrock Response Received!")
        source = "AWS Bedrock"
    except Exception as e:
        print(f"AWS Bedrock unavailable: {str(e)[:100]}...")
        print("Using intelligent fallback system...")
        ai_analysis = get_lifecycle_fallback_recommendation(sample_lifecycle_summary, attendees, open_gates)
        source = "Intelligent Fallback"
    
    print()
    print(f"AI Analysis Results (Source: {source}):")
    print("=" * 50)
    
    print(f"Overall Assessment:")
    print(f"   {ai_analysis['overall_assessment']}")
    print()
    
    print(f"Critical Phase: {ai_analysis['critical_phase'].replace('_', ' ').title()}")
    print()
    
    print(f"Recommendations:")
    for i, rec in enumerate(ai_analysis['recommendations'], 1):
        print(f"   {i}. {rec['recommendation']}")
        print(f"      Reason: {rec['reason']}")
        if 'impact_phases' in rec:
            print(f"      Impact: {', '.join(rec['impact_phases'])}")
        print()
    
    print(f"Optimized Parameters:")
    params = ai_analysis['optimized_parameters']
    print(f"   - Recommended Gates: {params['recommended_open_gates']}")
    print(f"   - Recommended Staff: {params['recommended_staff']}")
    print(f"   - Staggered Entry: {params['staggered_entry']}")
    print(f"   - Additional Exits: {params['additional_exits']}")
    print()
    
    print("AWS Integration Test Complete!")
    print(f"System successfully provides AI recommendations via {source}")

if __name__ == "__main__":
    test_aws_integration()