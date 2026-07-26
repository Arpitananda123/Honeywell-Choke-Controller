import os
import joblib
import numpy as np
import pandas as pd

class EliteAutonomousController:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "..", "models", "dynamic_well_model.pkl")
        self.model = joblib.load(model_path)
        
        # Absolute safety limits (Constraints)
        self.hard_min_whp = 220.0
        self.hard_min_flp = 160.0
        self.hard_min_bhp = 2900.0
        self.max_ramp = 5.0
        
        # Feedback Correction State
        self.last_prediction = None
        self.bias = {'q': 0.0, 'whp': 0.0, 'flp': 0.0, 'bhp': 0.0}

    def update_bias(self, current_q, current_whp, current_flp, current_bhp):
        if self.last_prediction is not None:
            self.bias['q'] = 0.5 * self.bias['q'] + 0.5 * (current_q - self.last_prediction['q'])
            self.bias['whp'] = 0.5 * self.bias['whp'] + 0.5 * (current_whp - self.last_prediction['whp'])
            self.bias['flp'] = 0.5 * self.bias['flp'] + 0.5 * (current_flp - self.last_prediction['flp'])
            self.bias['bhp'] = 0.5 * self.bias['bhp'] + 0.5 * (current_bhp - self.last_prediction['bhp'])

    def predict_with_bias(self, current_state_df):
        preds = self.model.predict(current_state_df)
        return (preds[:, 0] + self.bias['q'], preds[:, 1] + self.bias['whp'],
                preds[:, 2] + self.bias['flp'], preds[:, 3] + self.bias['bhp'])

    def get_optimal_move(self, current_q, current_whp, current_flp, current_bhp, current_choke, target_q):
        self.update_bias(current_q, current_whp, current_flp, current_bhp)
        
        min_move = max(0.0, current_choke - self.max_ramp)
        max_move = min(100.0, current_choke + self.max_ramp)
        candidates = np.arange(min_move, max_move + 0.1, 0.5)
        
        best_candidate = current_choke
        lowest_cost = float('inf')
        
        for candidate in candidates:
            X_step1 = pd.DataFrame([[current_q, current_whp, current_flp, current_bhp, candidate]], 
                                   columns=['OilRate_bbl_hr', 'WHP_psi', 'FLP_psi', 'BHP_psi', 'Next_Choke'])
            q1, whp1, flp1, bhp1 = self.predict_with_bias(X_step1)
            
            
            # LAGRANGIAN OBJECTIVE COST FUNCTION
            # Base Objective: Minimize error between target and predicted flow rate
            base_cost = abs(target_q - q1[0])
            
            # Penalty Weights: Massive mathematical penalty for constraint violations
            penalty = 0.0
            if whp1[0] < self.hard_min_whp: penalty += (self.hard_min_whp - whp1[0]) * 10000
            if flp1[0] < self.hard_min_flp: penalty += (self.hard_min_flp - flp1[0]) * 10000
            if bhp1[0] < self.hard_min_bhp: penalty += (self.hard_min_bhp - bhp1[0]) * 10000
            
            total_cost = base_cost + penalty
            
            # The optimizer searches for the candidate with the lowest possible cost
            if total_cost < lowest_cost:
                lowest_cost = total_cost
                best_candidate = candidate
                self.temp_prediction = {'q': q1[0], 'whp': whp1[0], 'flp': flp1[0], 'bhp': bhp1[0]}

        self.last_prediction = self.temp_prediction
        return best_candidate