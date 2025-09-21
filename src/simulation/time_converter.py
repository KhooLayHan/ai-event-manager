from datetime import datetime, timedelta

class TimeConverter:
    """
    A helper class to convert between real-world event times and
    simulation step counts.
    """
    def __init__(self, start_time_str: str, scale_factor: int):
        """
        Initializes the converter.

        Args:
            start_time_str (str): The event's start time in "HH:MM" format.
            scale_factor (int): How many simulation steps represent one real minute.
        """
        self.start_time = datetime.strptime(start_time_str, "%H:%M")
        self.scale_factor = scale_factor

    def to_step(self, time_str: str) -> int:
        """Converts a real-world time string into a simulation step number."""
        event_time = datetime.strptime(time_str, "%H:%M")
        delta_minutes = (event_time - self.start_time).total_seconds() / 60
        return int(delta_minutes * self.scale_factor)
    
    def to_real_time(self, step: int) -> str:
        """Converts a simulation step back to real-world time string."""
        minutes_elapsed = step / self.scale_factor
        real_time = self.start_time + timedelta(minutes=minutes_elapsed)
        return real_time.strftime("%H:%M")