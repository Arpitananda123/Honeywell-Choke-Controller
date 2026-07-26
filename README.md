# 🛢️ Autonomous Production Choke Controller (Honeywell MPC)

[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Deployed_on-Streamlit-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-4CAF50.svg?style=for-the-badge)](#)
[![Control Systems](https://img.shields.io/badge/Control_Logic-Lagrangian_MPC-8A2BE2.svg?style=for-the-badge)](#)

> **An enterprise-grade Model Predictive Control (MPC) system designed to autonomously optimize oil well production using machine learning and advanced constraint enforcement.**

---

## 📖 Project Overview

In industrial oil and gas operations, safely managing a well's production choke is a highly complex, multi-variable optimization problem. This project replaces traditional, manual heuristic control with an **Autonomous Digital Twin and MPC Optimizer**. 

The system autonomously evaluates candidate choke movements in real-time to maximize the target oil flow rate ($Q$) while mathematically preventing catastrophic pressure breaches in the Wellhead (WHP), Flowline (FLP), and Bottom-Hole (BHP).

### 🚀 Live Interactive Dashboard
**👉 [Launch the Live Streamlit Controller Here](https://your-streamlit-url-here.streamlit.app/)**
*(Note: An interactive cloud-deployment of this controller's logic)*

---

## 🧠 System Architecture

To ensure scalability and industrial reliability, the solution was engineered in four distinct phases:

### 1️⃣ Physics Simulation & Data Generation
* **Action:** Built a Python environment simulating the dynamic, non-linear physics of a single naturally flowing well.
* **Output:** Executed a 5,000-hour APRBS (Amplitude Pseudo-Random Binary Sequence) step-test to generate a rich, randomized time-series dataset.

### 2️⃣ The Digital Twin (Machine Learning)
* **Action:** Replaced hard-coded physics equations with a **Multi-Output Random Forest Regressor**.
* **Output:** The model consumes current well states at time $t$ and accurately predicts pressure responses at time $t+1$ for any proposed choke position. 

### 3️⃣ The Optimizer (Lagrangian MPC)
* **Action:** Developed a brute-force optimization loop that evaluates all safe choke movements ($\pm 5\%$ per hour). 
* **Output:** Utilizes a **Lagrangian Penalty Function** to calculate a "Cost" for every move. Safe moves have a penalty of zero; however, if a candidate move violates a pressure constraint, a massive penalty is applied ($+10,000$), mathematically forcing the AI to reject it.

### 4️⃣ Cloud-Native Deployment
* **Action:** Containerized the prediction logic and user interface using **Streamlit**.
* **Output:** Proves that intensive ML computations can be hosted centrally in the cloud while instantly beaming safe choke commands to edge-devices or operator tablets.

---

## 📈 Benchmark Scenario Results

The control system was rigorously tested against three standard operational scenarios. The plotted results can be found in the `/plots` directory:

| Scenario | Objective | Controller Response |
| :--- | :--- | :--- |
| **Scenario A** | Startup to 100 bbl/hr | Successfully ramped production from startup, settling perfectly on target with zero overshoot. |
| **Scenario B** | Step Change (100 $\to$ 150) | Immediately tracked dynamic operational changes without violating constraints. |
| **Scenario C** | **Infeasible Target (300 bbl/hr)** | **Safely rejected the target.** The Lagrangian penalty mathematically blocked the choke from opening further, settling precisely on the absolute pressure boundary. |

---

## ⚙️ Local Installation & Usage

Want to run the simulation, train the model, or launch the dashboard on your own machine? Follow these exact steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/Arpitananda123/Honeywell-Choke-Controller.git](https://github.com/Arpitananda123/Honeywell-Choke-Controller.git)
cd Honeywell-Choke-Controller
