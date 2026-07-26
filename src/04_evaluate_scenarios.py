import os
import matplotlib.pyplot as plt
from tqdm import tqdm
from simulator_interface import SimulatorWrapper
from phase3_mpc_controller import EliteAutonomousController # Note: Rename your Phase 3 file to phase3_mpc_controller.py if you haven't

def run_scenario(scenario_name, target_profile, total_hours, output_image):
    print(f"\n--- Running {scenario_name} ---")
    sim = SimulatorWrapper()
    controller = EliteAutonomousController()
    
    # Startup conditions
    current_choke = 30.0
    q, whp, flp, bhp = sim.step(current_choke)
    
    history = {'Time': [], 'Target_Q': [], 'Actual_Q': [], 'WHP': [], 'FLP': [], 'BHP': [], 'Choke': []}
    
    for hour in tqdm(range(total_hours)):
        target_q = target_profile(hour)
        
        # 1. Controller decides the next move
        current_choke = controller.get_optimal_move(q, whp, flp, bhp, current_choke, target_q)
        
        # 2. Simulator executes the move
        q, whp, flp, bhp = sim.step(current_choke)
        
        # 3. Log data
        history['Time'].append(hour)
        history['Target_Q'].append(target_q)
        history['Actual_Q'].append(q)
        history['WHP'].append(whp)
        history['FLP'].append(flp)
        history['BHP'].append(bhp)
        history['Choke'].append(current_choke)
        
    plot_results(scenario_name, history, output_image)

def plot_results(scenario_name, hist, output_image):
    """Generates the exact trend plots requested in the rubric."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    fig.suptitle(f"{scenario_name} Results", fontsize=16, fontweight='bold')
    
    # Plot 1: Target vs Actual Q
    axes[0].plot(hist['Time'], hist['Target_Q'], 'k--', label='Target Q')
    axes[0].plot(hist['Time'], hist['Actual_Q'], 'b-', label='Actual Q')
    axes[0].set_ylabel('Oil Rate (bbl/hr)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Constraints (Pressures)
    axes[1].plot(hist['Time'], hist['WHP'], 'r-', label='WHP')
    axes[1].plot(hist['Time'], hist['FLP'], 'orange', label='FLP')
    axes[1].plot(hist['Time'], hist['BHP'], 'g-', label='BHP')
    # Draw safe limits
    axes[1].axhline(y=220, color='r', linestyle=':', alpha=0.5)
    axes[1].axhline(y=160, color='orange', linestyle=':', alpha=0.5)
    axes[1].axhline(y=2900, color='g', linestyle=':', alpha=0.5)
    axes[1].set_ylabel('Pressures (psi)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Choke Position
    axes[2].plot(hist['Time'], hist['Choke'], 'k-', drawstyle='steps-post')
    axes[2].set_ylabel('Choke (%)')
    axes[2].set_xlabel('Time (Hours)')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_image), exist_ok=True)
    plt.savefig(output_image, dpi=300)
    print(f"Saved plot to {output_image}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Scenario A: Startup to Target (Hit 100 bbl/hr and stay there)
    run_scenario(
        "Scenario A - Startup", 
        target_profile=lambda t: 100.0, 
        total_hours=50, 
        output_image=os.path.join(script_dir, "..", "plots", "scenario_A.png")
    )
    
    # Scenario B: Target Tracking (Start at 100, jump to 150 at hour 30)
    run_scenario(
        "Scenario B - Target Tracking", 
        target_profile=lambda t: 100.0 if t < 30 else 150.0, 
        total_hours=80, 
        output_image=os.path.join(script_dir, "..", "plots", "scenario_B.png")
    )
    
    # Scenario C: Infeasible Target (Ask for 300 bbl/hr, force controller to settle safely)
    run_scenario(
        "Scenario C - Infeasible Target", 
        target_profile=lambda t: 300.0, 
        total_hours=60, 
        output_image=os.path.join(script_dir, "..", "plots", "scenario_C.png")
    )