import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

data = pd.read_csv('churn_data.csv')
X = data[['item_status','on_time','feedback']]
y = data['churn']

model = RandomForestClassifier(n_estimators=100, random_state=42)

model.fit(X, y)

with open('churn.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)
