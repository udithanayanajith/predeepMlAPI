import pandas as pd
from flask import Flask, request, jsonify
import pickle
from flask_cors import CORS 
import pymysql.cursors

app = Flask(__name__)
CORS(app)

db_config = {
    "host": "dcsrp-db-01.cvqssef8vzgx.ap-southeast-1.rds.amazonaws.com",
    "port":3306,
    "user": "dcsrp_pradeep",
    "password": "v4Dw4swkpKco4QuDdLz7yeM3HHjiaPeg",
    "db": "dcsrp_db",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

conn = None 

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to the MySQL database")
except Exception as e:
    print("Error:", str(e))
finally:
    if conn:
        conn.close()

with open('delivery.pkl', 'rb') as model_file:
    model = pickle.load(model_file)
with open('churn.pkl', 'rb') as model_file:
    churnModel = pickle.load(model_file)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        request_data = request.get_json()

        skill_mapping = {"Good": 1, "Average": 2, "Bad": 3}
        traffic_mapping = {"low": 3, "middle": 2, "high": 1}
        
        driver_skill = skill_mapping.get(request_data["driver_skill"], 2) 
        traffic_condition = traffic_mapping.get(request_data["traffic_condition"], 2)  
        data = {'skill': [driver_skill], 'traffic': [traffic_condition]}
        df = pd.DataFrame(data)
        proba = model.predict_proba(df)[0][1]  
        proba_percentage = int(proba * 100) 
          
        result = {
            "probability": proba_percentage
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/churnPredict', methods=['POST'])
def churnpredict():
    try:
        request_data = request.get_json()
        item_status_mapping = {"Damaged": 1, "Not-Damaged": 0}
        item_feedback_mapping = {"Unsatisifed": 0, "Satisfied": 1}
        item_status = item_status_mapping.get(request_data["status"],0) 
        item_feedback = item_feedback_mapping.get(request_data["feedback"])  
        item_onTime=request_data["ontime"]
        data = {"item_status": [item_status], "on_time": [item_onTime], "feedback": [item_feedback]}
        df = pd.DataFrame(data)
        proba = churnModel.predict(df)  
        proba_percentage = int(proba*10)
        result = {
            "probability": proba_percentage
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)})
    

@app.route("/savePred", methods=["PUT"])
def update_data():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        data = request.json
        id=data["id"]
        driver_skill = data["driver_skill"]
        traffic_condition = data["traffic_condition"]
        success = data["success"]

        update_query = (
            "UPDATE order_details SET driver_skill = %s, traffic_condition = %s, success = %s WHERE id = %s"
        )

        cursor.execute(update_query, (driver_skill, traffic_condition, success, id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Data updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run()
