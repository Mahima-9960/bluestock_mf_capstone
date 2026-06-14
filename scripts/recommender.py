import pandas as pd
import numpy as np
import sys

def recommend_funds(risk_appetite):
    risk_profile = risk_appetite.strip().lower()
    
    # Load or mock matching structural fund database profiles
    np.random.seed(10)
    schemes = [f"Bluestock Alpha Scheme {i}" for i in range(1, 16)]
    grades = ['low', 'moderate', 'high'] * 5
    sharpes = np.random.uniform(0.65, 1.95, 15)
    
    df = pd.DataFrame({'fund_name': schemes, 'risk_grade': grades, 'sharpe_ratio': np.round(sharpes, 2)})
    
    # Filter allocations matching user boundaries
    filtered_df = df[df['risk_grade'] == risk_profile]
    
    if filtered_df.empty:
        print("❌ Choice error: Please insert a valid profile string (Low / Moderate / High).")
        return
        
    top_3 = filtered_df.sort_values(by='sharpe_ratio', ascending=False).head(3)
    
    print(f"\n================ TOP 3 MATCHING FUNDS: [{risk_appetite.upper()}] ================")
    print(top_3.to_string(index=False))
    print("======================================================================\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        recommend_funds(sys.argv[1])
    else:
        user_choice = input("Enter Risk Profile Appetite (Low / Moderate / High): ")
        recommend_funds(user_choice)