import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from simulator_interface import SimulatorWrapper

def generate_step_test_sequence(total_hours):
    """
    Generates a randomized sequence of choke targets, holding them for 
    varying durations to capture steady-state dynamics.
    Enforces the +-5% max ramp rate and 0-100% boundary constraints.
    """
    np.random.seed(42)
    sequence = []
    current_hour = 0
    current_choke = 30.0  # Starting choke position

    while current_hour < total_hours:
        # Pick a random target between 20% and 80% to avoid immediate constraint crashes
        target_choke = np.random.uniform(20.0, 80.0)
        # Hold this target for anywhere between 5 and 30 hours
        hold_time = int(np.random.uniform(5, 30))

        for _ in range(hold_time):
            if current_hour >= total_hours:
                break
            
            # Enforce Ramp Rate Constraint: Max +- 5% per step
            if target_choke > current_choke + 5.0:
                current_choke += 5.0
            elif target_choke < current_choke - 5.0:
                current_choke -= 5.0
            else:
                current_choke = target_choke
                
            # Enforce absolute boundaries (0% to 100%)
            current_choke = max(0.0, min(100.0, current_choke))

            sequence.append(current_choke)
            current_hour += 1

    return sequence

def run_experiment(total_hours=5000):
    """
    Executes the step-test on the simulator and logs all state variables to a CSV.
    """
    # 1. Find exactly where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 2. Go up one level to the root, then into the data folder
    output_file = os.path.join(script_dir, "..", "data", "my_generated_step_data.csv")
    
    print(f"Generating {total_hours}-hour open-loop step-test sequence...")
    choke_sequence = generate_step_test_sequence(total_hours)
    
    sim = SimulatorWrapper()
    records = []

    print("Running simulator process...")
    for hour in tqdm(range(total_hours)):
        u = choke_sequence[hour]
        
        # Interface with simulator: Q, WHP, FLP, BHP = simulator.step(u)
        q, whp, flp, bhp = sim.step(u)
        
        records.append({
            'Time_hr': hour,
            'Choke_pct': round(u, 2),
            'OilRate_bbl_hr': round(q, 2),
            'WHP_psi': round(whp, 2),
            'FLP_psi': round(flp, 2),
            'BHP_psi': round(bhp, 2)
        })

    # Ensure output directory exists based on the foolproof path
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save to DataFrame and CSV
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    
    # Print the exact location so we can verify it
    print(f"\nExperiment complete! Data successfully saved to:\n{os.path.abspath(output_file)}")
    print(df.head())

if __name__ == "__main__":
    run_experiment(total_hours=5000)