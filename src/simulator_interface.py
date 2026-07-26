import numpy as np

class SimulatorWrapper:
    """
    Wrapper for the Honeywell well simulator.
    Currently uses a mock physics model so you can build the pipeline immediately.
    """
    def __init__(self):
        # Initial steady-state values
        self.q = 90.0
        self.whp = 250.0
        self.flp = 180.0
        self.bhp = 3000.0

    def step(self, choke_position):
        """
        Simulates one control interval (1 hour).
        Returns: Q, WHP, FLP, BHP
        """
        # --- MOCK PHYSICS ENGINE ---
        # If you find the actual simulator file, delete this mock logic 
        # and replace with: return official_simulator.step(choke_position)
        
        # Calculate target steady-states based on choke position
        target_q = 20.0 + 2.1 * choke_position
        target_whp = 280.0 - 0.9 * choke_position
        target_flp = 200.0 - 0.6 * choke_position
        target_bhp = 3200.0 - 4.2 * choke_position

        # Apply a first-order dynamic lag to simulate settling time (process behavior)
        alpha = 0.3
        self.q += alpha * (target_q - self.q) + np.random.normal(0, 0.5)
        self.whp += alpha * (target_whp - self.whp) + np.random.normal(0, 1.0)
        self.flp += alpha * (target_flp - self.flp) + np.random.normal(0, 0.8)
        self.bhp += alpha * (target_bhp - self.bhp) + np.random.normal(0, 2.0)

        return self.q, self.whp, self.flp, self.bhp 