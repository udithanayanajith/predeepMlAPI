import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

data = pd.read_csv('dataset.csv')
X = data[['skill', 'traffic']]
y = data['pred']

model = RandomForestClassifier(n_estimators=100, random_state=42)

model.fit(X, y)

with open('delivery.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)
