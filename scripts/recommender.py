import pandas as pd
import os

def recommend_funds(risk_appetite):
    """
    Recommends top 3 funds based on the user's risk appetite: 'Low', 'Moderate', or 'High'.
    """
    try:
        # Step A: Point to the exact location of your data file
        # We use '../datasets/' because this script is inside the 'scripts' folder!
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, '../datasets/clean_performance.csv')
        
        # Step B: Load the data
        df = pd.read_csv(file_path)
        
        # Step C: Filter for the chosen risk grade
        filtered_df = df[df['risk_grade'].str.lower() == risk_appetite.lower()]
        
        if filtered_df.empty:
            return f"No funds found for the risk profile: {risk_appetite}"
            
        # Step D: Sort by the best Sharpe Ratio and grab the top 3
        top_3 = filtered_df.sort_values(by='sharpe_ratio', ascending=False).head(3)
        
        print(f"\n--- Top 3 {risk_appetite.capitalize()}-Risk Fund Recommendations ---")
        return top_3[['scheme_name', 'category', 'return_3yr_pct', 'sharpe_ratio']]
        
    except FileNotFoundError:
        return "Error: Could not find clean_performance.csv in the datasets folder!"
    except Exception as e:
        return f"An error occurred: {e}"

# --- This block allows us to test the script right now ---
if __name__ == "__main__":
    print("Testing the Recommender System...")
    # Let's test what happens when an investor wants "Moderate" risk
    result = recommend_funds('Moderate')
    print(result)