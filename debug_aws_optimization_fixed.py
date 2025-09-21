#!/usr/bin/env python3
"""
Debug test for AWS optimization suggestions accuracy
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

import json
import logging
from src.aws.lifecycle_bedrock_fixed import get_full_lifecycle_ai_analysis
from src.aws.lifecycle_bedrock_fixed import get_lifecycle_fallback_recommendation

# Enable detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_aws_optimization_accuracy():
    """Test AWS optimization with various scenarios"""
    
    print("DEBUGGING AWS OPTIMIZATION ACCURACY")
    print("=" * 60)
    
    # Test scenarios with different severity levels
    test_scenarios = [
        {
            "name": "CRITICAL CONGESTION SCENARIO",
            "attendees": 2000,
            "gates": 2,
            "lifecycle_summary": {
                "entry_rush": {
                    "peak_congestion_percent": 95.5,
                    "avg_entry_time_mins": 35,
                    "max_wait_time_mins": 45,
                    "entry_success_rate": 15.2,
                    "wait_time_distribution": {"0-5min": 50, "5-10min": 200, "10-15min": 800, "15+min": 950},
                    "duration_steps": 100
                },
                "mid_event": {
                    "peak_congestion_percent": 78.3,
                    "avg_wait_time_mins": 25,
                    "entry_success_rate": 25.8,
                    "duration_steps": 200
                },
                "evacuation": {
                    "peak_congestion_percent": 98.1,
                    "evacuation_time_seconds": 450,
                    "entry_success_rate": 35.0,
                    "duration_steps": 150
                }
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\nTEST {i}: {scenario['name']}")
        print("-" * 40)
        
        # Print input data
        print(f"Input Data:")
        print(f"  Attendees: {scenario['attendees']}")
        print(f"  Gates: {scenario['gates']}")
        print(f"  Entry Congestion: {scenario['lifecycle_summary']['entry_rush']['peak_congestion_percent']:.1f}%")
        print(f"  Entry Wait Time: {scenario['lifecycle_summary']['entry_rush']['avg_entry_time_mins']} min")
        print(f"  Entry Success: {scenario['lifecycle_summary']['entry_rush']['entry_success_rate']:.1f}%")
        print(f"  Evacuation Time: {scenario['lifecycle_summary']['evacuation']['evacuation_time_seconds']} sec")
        
        # Test AWS Bedrock
        print(f"\nTesting AWS Bedrock...")
        try:
            aws_result = get_full_lifecycle_ai_analysis(
                scenario['lifecycle_summary'], 
                scenario['attendees'], 
                scenario['gates']
            )
            print(f"AWS Bedrock Response:")
            print(f"  Critical Phase: {aws_result['critical_phase']}")
            print(f"  Assessment: {aws_result['overall_assessment'][:100]}...")
            
            # Check optimization parameters
            params = aws_result['optimized_parameters']
            print(f"  Recommended Gates: {scenario['gates']} -> {params.get('recommended_entrance_gates', 'N/A')}")
            print(f"  Recommended Staff: 20 -> {params.get('recommended_staff', 'N/A')}")
            print(f"  Optimal Attendees: {params.get('optimal_attendee_capacity', 'N/A')}")
            
            # Validate recommendations make sense
            validate_recommendations(scenario, aws_result, "AWS Bedrock")
            
        except Exception as e:
            print(f"AWS Bedrock failed: {str(e)[:100]}...")
            
            # Test fallback
            print(f"Testing Fallback System...")
            fallback_result = get_lifecycle_fallback_recommendation(
                scenario['lifecycle_summary'], 
                scenario['attendees'], 
                scenario['gates']
            )
            print(f"Fallback Response:")
            print(f"  Critical Phase: {fallback_result['critical_phase']}")
            print(f"  Assessment: {fallback_result['overall_assessment'][:100]}...")
            
            # Check optimization parameters
            params = fallback_result['optimized_parameters']
            print(f"  Recommended Gates: {scenario['gates']} -> {params.get('recommended_entrance_gates', 'N/A')}")
            print(f"  Recommended Staff: 20 -> {params.get('recommended_staff', 'N/A')}")
            print(f"  Optimal Attendees: {params.get('optimal_attendee_capacity', 'N/A')}")
            
            # Validate recommendations make sense
            validate_recommendations(scenario, fallback_result, "Fallback")

def validate_recommendations(scenario, ai_result, source):
    """Validate that AI recommendations make logical sense"""
    print(f"\nVALIDATION for {source}:")
    
    entry_data = scenario['lifecycle_summary']['entry_rush']
    evacuation_data = scenario['lifecycle_summary']['evacuation']
    params = ai_result['optimized_parameters']
    
    issues = []
    
    # Check if high congestion leads to more gates
    if entry_data['peak_congestion_percent'] > 70:
        recommended_gates = params.get('recommended_entrance_gates', scenario['gates'])
        if recommended_gates <= scenario['gates']:
            issues.append(f"High congestion ({entry_data['peak_congestion_percent']:.1f}%) but no gate increase recommended")
        else:
            print(f"High congestion correctly addressed with more gates")
    
    # Check if long wait times lead to more staff
    if entry_data['avg_entry_time_mins'] > 15:
        recommended_staff = params.get('recommended_staff', 20)
        if recommended_staff <= 20:
            issues.append(f"Long wait times ({entry_data['avg_entry_time_mins']} min) but no staff increase")
        else:
            print(f"Long wait times correctly addressed with more staff")
    
    # Check if low entry success leads to capacity reduction
    if entry_data['entry_success_rate'] < 30:
        optimal_attendees = params.get('optimal_attendee_capacity', scenario['attendees'])
        if optimal_attendees >= scenario['attendees']:
            issues.append(f"Low entry success ({entry_data['entry_success_rate']:.1f}%) but no attendee reduction")
        else:
            print(f"Low entry success correctly addressed with attendee reduction")
    
    # Check if slow evacuation leads to more exits
    if evacuation_data['evacuation_time_seconds'] > 300:
        recommended_exits = params.get('recommended_exit_gates', scenario['gates'])
        if recommended_exits <= scenario['gates']:
            issues.append(f"Slow evacuation ({evacuation_data['evacuation_time_seconds']}s) but no exit increase")
        else:
            print(f"Slow evacuation correctly addressed with more exits")
    
    # Print validation results
    if issues:
        print(f"VALIDATION ISSUES FOUND:")
        for issue in issues:
            print(f"    {issue}")
    else:
        print(f"All validations passed - recommendations are logical!")
    
    return len(issues) == 0

if __name__ == "__main__":
    test_aws_optimization_accuracy()