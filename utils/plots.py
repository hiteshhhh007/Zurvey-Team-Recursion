import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

df = pd.read_csv("train-all.csv")

thresholds = list(range(-2, 13))
accuracy_list = []
precision_list = []
recall_list = []
f1_list = []

for threshold in thresholds:
    df["Quality_Flag_Predicted"] = df["Combined_Total_Score"].apply(lambda x: 0 if x > threshold else 1)
    
    y_true = df["OE_Quality_Flag"]
    y_pred = df["Quality_Flag_Predicted"]

    accuracy_list.append(accuracy_score(y_true, y_pred))
    precision_list.append(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    recall_list.append(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    f1_list.append(f1_score(y_true, y_pred, average="weighted", zero_division=0))

# Plot the metrics
plt.figure(figsize=(10, 6))
plt.plot(thresholds, accuracy_list, marker='o', label="Accuracy")
plt.plot(thresholds, precision_list, marker='s', label="Precision")
plt.plot(thresholds, recall_list, marker='^', label="Recall")
plt.plot(thresholds, f1_list, marker='d', label="F1-Score")

plt.xlabel("Threshold")
plt.ylabel("Score")
plt.title("Model Performance vs. Threshold")
plt.legend()
plt.grid()
plt.show()
