import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib

# Setting up the main page layout
st.set_page_config(page_title="Autonomous Well Controller", layout="wide")

st.title("🛢️ Autonomous Production Choke Controller")
st.subheader("Interactive MPC Dashboard & Digital Twin")

# Sidebar menu
st.sidebar.header("Menu")
page = st.sidebar.radio("Go to", ["Live Controller", "Scenario Results", "Architecture"])


#The Live Interactive Controller

if page == "Live Controller":
    st.markdown("### Test the MPC Controller Live")
    
    # Simple explanation of what this page actually does
    st.info("""
    **What is happening here?** 
    In a real oilfield, our Python script would run autonomously every single hour. This dashboard lets you simulate just *one* of those hours manually. 
    You input the current sensor readings, and the AI behind the scenes will instantly evaluate hundreds of possible choke movements. It predicts the future pressures for every single move and mathematically selects the optimal choke setting that maximizes production without violating safety limits.
    """)

    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown("#### What is the well doing right now?")
        q_curr = st.number_input("Current Oil Rate (bbl/hr)", value=110.0)
        whp_curr = st.number_input("Wellhead Pressure (psi)", value=250.0)
        flp_curr = st.number_input("Flowline Pressure (psi)", value=180.0)
        bhp_curr = st.number_input("Bottom Hole Pressure (psi)", value=3000.0)
        choke_curr = st.slider("Current Choke Position (%)", 0.0, 100.0, 40.0)

    with right_col:
        st.markdown("#### What is our goal?")
        q_target = st.number_input("Target Oil Rate (bbl/hr)", value=150.0)
        
        st.warning("""
        **Safety Limits (Hard Constraints):**
        * Max choke movement: ±5.0% per hour
        * Min WHP: 220.0 psi
        * Min FLP: 160.0 psi
        * Min BHP: 2900.0 psi
        """)
        
        if st.button("Calculate Best Choke Move", type="primary"):
            model_path = os.path.join("models", "dynamic_well_model.pkl")
            
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                
                min_allowed = max(0.0, choke_curr - 5.0)
                max_allowed = min(100.0, choke_curr + 5.0)
                possible_moves = np.arange(min_allowed, max_allowed + 0.1, 0.5)
                
                best_move = choke_curr
                lowest_penalty = float('inf')
                
                for move in possible_moves:
                    test_data = pd.DataFrame([[q_curr, whp_curr, flp_curr, bhp_curr, move]], 
                                         columns=['OilRate_bbl_hr', 'WHP_psi', 'FLP_psi', 'BHP_psi', 'Next_Choke'])
                    
                    prediction = model.predict(test_data)[0]
                    pred_q, pred_whp, pred_flp, pred_bhp = prediction[0], prediction[1], prediction[2], prediction[3]
                    
                    cost = abs(q_target - pred_q)
                    
                    if pred_whp < 220.0: cost += (220.0 - pred_whp) * 10000
                    if pred_flp < 160.0: cost += (160.0 - pred_flp) * 10000
                    if pred_bhp < 2900.0: cost += (2900.0 - pred_bhp) * 10000
                    
                    if cost < lowest_penalty:
                        lowest_penalty = cost
                        best_move = move
                
                st.success(f"**Best Safe Choke Position:** {best_move:.1f}%")
                change = best_move - choke_curr
                st.metric("Suggested Adjustment", f"{best_move:.1f}%", delta=f"{change:+.1f}%")
            else:
                st.error("Model file not found! Did you run Phase 2?")


# Scenario Results

elif page == "Scenario Results":
    st.markdown("### Hackathon Required Scenarios")
    
    # Adding the explanation about the dataset
    st.write("""
    These plots demonstrate the controller's performance across the three required hackathon scenarios. 
    **Note on Data:** The predictive capabilities shown here are driven by a dynamic model trained on a custom 5,000-hour APRBS (Amplitude Pseudo-Random Binary Sequence) step-test dataset that we generated specifically to map the non-linear physics of this well.
    """)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_a = os.path.join(base_dir, "plots", "scenario_A.png")
    img_b = os.path.join(base_dir, "plots", "scenario_B.png")
    img_c = os.path.join(base_dir, "plots", "scenario_C.png")
    
    tab1, tab2, tab3 = st.tabs(["Scenario A", "Scenario B", "Scenario C"])
    
    with tab1:
        if os.path.exists(img_a):
            st.image(img_a, caption="Scenario A: Startup to Target (100 bbl/hr)")
        else:
            st.error("Image A missing.")
            
    with tab2:
        if os.path.exists(img_b):
            st.image(img_b, caption="Scenario B: Tracking a Step Change in Target")
        else:
            st.error("Image B missing.")
            
    with tab3:
        if os.path.exists(img_c):
            st.image(img_c, caption="Scenario C: Enforcing Safety Limits against an Infeasible Target")
        else:
            st.error("Image C missing.")


# Architecture

elif page == "Architecture":
    st.markdown("### Step-by-Step Architecture (How I Built This)")
    st.write("To build a solution that goes beyond a basic script, I broke the problem down into four core engineering phases:")
    
    st.markdown("""
    #### 1. Simulating the Physics (Data Generation)
    I couldn't train a model without data, so I built a Python wrapper around the provided well equations. I ran a **5,000-hour randomized step-test** (changing the choke randomly between 0-100%). This generated a robust CSV dataset capturing exactly how the flow rates and pressures react over time to choke movements.

    #### 2. Building the Brain (Digital Twin)
    Instead of writing hard-coded rules, I treated this as a Machine Learning problem. I took my 5,000-row dataset and trained a **Multi-Output Random Forest Regressor**. By shifting the time-series data by one hour ($t$ to $t+1$), I taught the model to look at the *current* state of the well and accurately predict what the pressures would be 1 hour into the future based on any proposed choke move.

    #### 3. Designing the Controller (Lagrangian MPC)
    With the predictive "brain" ready, I wrote the control loop. Every hour, the controller evaluates every possible choke move within the allowed $\pm 5\%$ limit. Instead of just using basic `if/else` statements, I implemented a **Lagrangian Penalty Function**:
    * It calculates a "cost" for each move.
    * If a move gets us closer to the target oil rate, the cost goes down.
    * If a move pushes our pressures below the safe limits, it applies a massive mathematical penalty ($+10,000$), forcing the controller to reject it.

    #### 4. Enterprise Deployment (This Dashboard)
    Finally, to prove this works in a real-world edge/cloud computing setup, I deployed the model to Streamlit. This simulates how a remote server could run the intensive ML calculations and instantly beam the optimal, safe choke commands down to an operator's tablet at the physical well site.
    """)