import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def analyze_and_train():
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "..", "data", "my_generated_step_data.csv")
    model_path = os.path.join(script_dir, "..", "models", "dynamic_well_model.pkl")
    plot_path = os.path.join(script_dir, "..", "plots", "step_test_analysis.png")
    
    print("Loading Phase 1 Step-Test Data...")
    df = pd.read_csv(data_path)
    
    # GENERATES PRESENTATION PLOT (Open-Loop Analysis)
    
    print("Generating step-test analysis plot for presentation...")
    fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
    fig.suptitle("Open-Loop Step-Test Analysis", fontsize=14, fontweight='bold')
    
    plot_slice = df.iloc[500:800] # Take a clean 300-hour slice to show dynamics clearly
    
    axes[0].plot(plot_slice['Time_hr'], plot_slice['Choke_pct'], 'k-', drawstyle='steps-post')
    axes[0].set_ylabel("Choke (%)")
    axes[0].set_title("Manipulated Variable")
    
    axes[1].plot(plot_slice['Time_hr'], plot_slice['OilRate_bbl_hr'], 'b-')
    axes[1].set_ylabel("Oil Rate (bbl/hr)")
    axes[1].set_title("Primary Production Target")
    
    axes[2].plot(plot_slice['Time_hr'], plot_slice['WHP_psi'], 'r-', label="WHP")
    axes[2].plot(plot_slice['Time_hr'], plot_slice['FLP_psi'], 'orange', label="FLP")
    axes[2].set_ylabel("Surface Pressures")
    axes[2].legend(loc="upper right")
    
    axes[3].plot(plot_slice['Time_hr'], plot_slice['BHP_psi'], 'g-')
    axes[3].set_ylabel("Bottom Hole Pressure")
    axes[3].set_xlabel("Time (hours)")
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path, dpi=300)
    print(f"Plot saved to: {os.path.abspath(plot_path)}")
    
    
    # FEATURE ENGINEERING (State-Space Formulation)
    # To predict the future state (t+1), the model needs to know the 
    # CURRENT state (t) and the NEXT proposed choke movement (t+1).
    
    df['Next_Choke'] = df['Choke_pct'].shift(-1)
    df['Next_Q'] = df['OilRate_bbl_hr'].shift(-1)
    df['Next_WHP'] = df['WHP_psi'].shift(-1)
    df['Next_FLP'] = df['FLP_psi'].shift(-1)
    df['Next_BHP'] = df['BHP_psi'].shift(-1)
    
    df = df.dropna() # Drop the very last row which has no 'next' hour
    
    features = ['OilRate_bbl_hr', 'WHP_psi', 'FLP_psi', 'BHP_psi', 'Next_Choke']
    targets = ['Next_Q', 'Next_WHP', 'Next_FLP', 'Next_BHP']
    
    X = df[features]
    y = df[targets]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    
    
    # TRAIN THE DIGITAL TWIN

    print("\nTraining Multi-Output Random Forest Process Model...")
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    
    # VALIDATION METRICS (For the PPT slides)
    
    y_pred = model.predict(X_test)
    
    print("\n==========================================")
    print("MODEL VALIDATION METRICS")
    print("==========================================")
    for i, target in enumerate(targets):
        r2 = r2_score(y_test.iloc[:, i], y_pred[:, i])
        rmse = np.sqrt(mean_squared_error(y_test.iloc[:, i], y_pred[:, i]))
        print(f"{target.replace('Next_', '')} Prediction -> R2: {r2:.4f} | RMSE: {rmse:.2f}")
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"\nModel successfully saved to: {os.path.abspath(model_path)}")

if __name__ == "__main__":
    analyze_and_train()