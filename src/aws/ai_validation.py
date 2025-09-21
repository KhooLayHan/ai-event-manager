def validate_ai_suggestions(simulation_data: dict, ai_suggestions: dict, current_config: dict) -> dict:
    """
    Validate if AI suggestions are logically correct based on simulation data.
    
    Args:
        simulation_data: Real simulation metrics
        ai_suggestions: AI recommended parameters
        current_config: Current event configuration
        
    Returns:
        Validation results with corrections if needed
    """
    validation_results = {
        "is_valid": True,
        "issues": [],
        "corrected_suggestions": ai_suggestions.copy()
    }
    
    # Extract key metrics
    congestion = simulation_data.get('peak_congestion_percent', 0)
    wait_time = simulation_data.get('real_wait_time_mins', 0)
    entry_rate = simulation_data.get('entry_success_rate', 100)
    
    current_entrance_gates = current_config.get('entrance_gates', 2)
    current_exit_gates = current_config.get('exit_gates', 2)
    current_staff = current_config.get('staff_count', 20)
    attendees = current_config.get('attendees', 2000)
    
    # Validate entrance gate suggestions
    recommended_entrance = ai_suggestions.get('recommended_entrance_gates', current_entrance_gates)
    
    # Logic: If congestion >70% OR entry_rate <50%, should increase gates
    if congestion > 70 or entry_rate < 50:
        if recommended_entrance <= current_entrance_gates:
            validation_results["is_valid"] = False
            validation_results["issues"].append(
                f"High congestion ({congestion:.1f}%) or low entry rate ({entry_rate:.1f}%) "
                f"requires MORE entrance gates, but AI suggested {recommended_entrance} (same or less than current {current_entrance_gates})"
            )
            # Correct the suggestion
            validation_results["corrected_suggestions"]["recommended_entrance_gates"] = min(current_entrance_gates + 2, 6)
    
    # Validate staff suggestions
    recommended_staff = ai_suggestions.get('recommended_staff', current_staff)
    
    # Logic: If wait_time >10min, should increase staff significantly
    if wait_time > 10:
        min_staff_increase = max(10, int(wait_time - 10) * 2)
        if recommended_staff < current_staff + min_staff_increase:
            validation_results["is_valid"] = False
            validation_results["issues"].append(
                f"High wait time ({wait_time} min) requires significant staff increase, "
                f"but AI suggested {recommended_staff} (only +{recommended_staff - current_staff} from current {current_staff})"
            )
            # Correct the suggestion
            validation_results["corrected_suggestions"]["recommended_staff"] = current_staff + min_staff_increase
    
    # Validate capacity suggestions
    recommended_capacity = ai_suggestions.get('optimal_attendee_capacity', attendees)
    
    # Logic: If congestion >80% AND entry_rate <30%, should reduce capacity
    if congestion > 80 and entry_rate < 30:
        max_safe_capacity = int(attendees * 0.7)  # Reduce by 30%
        if recommended_capacity > max_safe_capacity:
            validation_results["is_valid"] = False
            validation_results["issues"].append(
                f"Critical congestion ({congestion:.1f}%) and low entry rate ({entry_rate:.1f}%) "
                f"requires capacity reduction, but AI suggested {recommended_capacity} (too high)"
            )
            # Correct the suggestion
            validation_results["corrected_suggestions"]["optimal_attendee_capacity"] = max_safe_capacity
    
    # Validate exit gate suggestions for evacuation
    recommended_exit = ai_suggestions.get('recommended_exit_gates', current_exit_gates)
    
    # Logic: Should have at least as many exit gates as entrance gates for safety
    if recommended_exit < recommended_entrance:
        validation_results["is_valid"] = False
        validation_results["issues"].append(
            f"Safety violation: Exit gates ({recommended_exit}) should be >= entrance gates ({recommended_entrance})"
        )
        # Correct the suggestion
        validation_results["corrected_suggestions"]["recommended_exit_gates"] = recommended_entrance
    
    # Check staff-to-attendee ratio
    staff_ratio = attendees / recommended_staff
    if staff_ratio > 150:  # More than 150 attendees per staff member
        validation_results["is_valid"] = False
        validation_results["issues"].append(
            f"Staff ratio too low: 1:{staff_ratio:.0f} (recommended max 1:150)"
        )
        # Correct the suggestion
        validation_results["corrected_suggestions"]["recommended_staff"] = max(recommended_staff, int(attendees / 150))
    
    return validation_results