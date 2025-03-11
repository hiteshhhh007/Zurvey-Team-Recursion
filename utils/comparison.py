import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

df=pd.read_csv('Final-Train-Predicted.csv')

y_true=df['OE_Quality_Flag']
y_pred=df['Quality_Flag_Predicted']

accuracy=accuracy_score(y_true,y_pred)
precision=precision_score(y_true,y_pred,average='weighted')
recall=recall_score(y_true,y_pred,average='weighted')
f1=f1_score(y_true,y_pred,average='weighted')

print(f'Accuracy: {accuracy:.4f}')
print(f'Precision: {precision:.4f}')
print(f'Recall: {recall:.4f}')
print(f'F1-score: {f1:.4f}')
