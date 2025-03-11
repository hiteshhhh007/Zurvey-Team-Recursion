import pandas as pd

# Read the CSV file
df = pd.read_csv("")

# Create the new column based on the condition
df["Quality_Flag_Predicted"] = df["Combined_Total_Score"].apply(lambda x: 0 if x > -1 else 1)

# Save the modified DataFrame back to a new CSV file
df.to_csv("", index=False)

print("CSV updated successfully!")
