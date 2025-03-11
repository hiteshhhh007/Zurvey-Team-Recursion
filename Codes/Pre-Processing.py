import pandas as pd
import re


file_path = ""
df = pd.read_csv(file_path)

columns_to_clean = ["Q16A", "Q16B", "Q18_1", "Q18_2", "Q18_3"]

def clean_text(text):
    if pd.isna(text):
        return ""  
    text = re.sub(r"[^a-zA-Z0-9\s]", "", str(text))  
    text = text.lower().strip()  
    text = re.sub(r"\s+", " ", text)  
    return text


df[columns_to_clean] = df[columns_to_clean].applymap(clean_text)


output_path = "preprocessed.csv"
df.to_csv(output_path, index=False)

print(f"Preprocessed CSV saved at: {output_path}")
