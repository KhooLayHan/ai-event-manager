# REAL BACKEND - Placeholder
def run_simulation_step_by_step(params):
    # The Simulation Engineer will replace this with their REAL logic.
    # For now, we yield the mock data so the test UI runs.
    from src.stubs.mock_backend import run_simulation_step_by_step as mock_run

    yield from mock_run(params)
