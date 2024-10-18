from flask import Flask, jsonify, request
import sqlite3

DATABASE_NAME = 'Database.db'

# Helper Functions for Flask app

def row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    data = {}
    for idx, col in enumerate(cursor.description):
        data[col[0]] = row[idx]
    return data

def execute_query(query, params=None):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.row_factory = row_to_dict

    if params:
        c.execute(query, params)
    else:
        c.execute(query)

    if query.strip().upper().startswith("SELECT"):
        results = c.fetchall()
    else:
        conn.commit()
        results = None

    conn.close()
    return results

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# 1. REGISTER USER
@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    name = data.get('Name')
    email = data.get('Email')
    password = data.get('Password')
    phone = data.get('Phone')

    if not all([name, email, password, phone]):
        return jsonify({'message': 'All fields are required'}), 400

    query = "INSERT INTO CUSTOMER(Name, Phone, Email, Password) VALUES (?, ?, ?, ?)"
    execute_query(query, (name, phone, email, password))

    return jsonify({'message': 'User registered successfully'}), 201

# 2. SIGN IN
@app.route("/signin", methods=['POST'])
def sign_in():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    query = "SELECT * FROM CUSTOMER WHERE Email = ? AND Password = ?"
    user = execute_query(query, (email, password))

    if user:
        return jsonify({'message': "Sign-in successful", 'user': user[0]}), 200
    else:
        return jsonify({'error': "Invalid email or password."}), 401

# 3. USER PROFILE
@app.route("/profile/<int:customer_id>", methods=['GET'])
def get_user_profile(customer_id):
    query = "SELECT Name, Email, Phone FROM CUSTOMER WHERE Cust_id = ?"
    user_profile = execute_query(query, (customer_id,))
    if user_profile:
        return jsonify({'profile': user_profile[0]}), 200
    return jsonify({'error': "User not found."}), 404

# 4. PRODUCT DETAILS (EVENT PLAN)
@app.route("/eventplan/<int:eventplan_id>", methods=['GET'])
def get_event_plan(eventplan_id):
    query = "SELECT * FROM EVENTPLAN WHERE EventPlan_id = ?"
    event_plan = execute_query(query, (eventplan_id,))
    if event_plan:
        return jsonify({'event_plan': event_plan[0]}), 200
    return jsonify({'error': "Event plan not found."}), 404

# 5. VIEW USER'S EVENT PLANS
@app.route("/user/<int:customer_id>/eventplans", methods=['GET'])
def get_user_event_plans(customer_id):
    query = "SELECT * FROM EVENTPLAN WHERE Cust_id = ?"
    event_plans = execute_query(query, (customer_id,))
    return jsonify({'event_plans': event_plans}), 200

# 6. VIEW VENDORS FOR EACH EVENT PLAN
@app.route("/eventplan/<int:eventplan_id>/vendors", methods=['GET'])
def get_event_plan_vendors(eventplan_id):
    query = """
    SELECT VENDOR.Name, VENDOR.Category 
    FROM VENDOR 
    JOIN TASKS ON VENDOR.Vendor_id = TASKS.Vendor_id 
    WHERE TASKS.EventPlan_id = ?
    """
    vendors = execute_query(query, (eventplan_id,))
    return jsonify({'vendors': vendors}), 200

# 7. VIEW THE STATUS OF TASKS FOR AN EVENT PLAN
@app.route("/eventplan/<int:eventplan_id>/tasks", methods=['GET'])
def get_event_plan_tasks(eventplan_id):
    query = "SELECT TASKS.Task_Details, TASKS.Task_Urgency FROM TASKS WHERE TASKS.EventPlan_id = ?"
    tasks = execute_query(query, (eventplan_id,))
    return jsonify({'tasks': tasks}), 200

# 8. ADD TO CART
@app.route("/cart/add", methods=['POST'])
def add_to_cart():
    data = request.get_json()
    eventplan_id = data.get('EventPlan_id')
    Status = data.get('Status')

    if not all([eventplan_id, Status]):
        return jsonify({'message': 'Status and Event Plan ID are required'}), 400

    query = "INSERT INTO CART (EventPlan_id, Status) VALUES (?, ?)"
    execute_query(query, ( eventplan_id, Status))

    return jsonify({'message': 'Event plan added to cart successfully'}), 201

# 9. HOMEPAGE (USER'S EVENT PLANS)
@app.route("/user/<int:customer_id>/homepage", methods=['GET'])
def get_user_homepage(customer_id):
    query = "SELECT * FROM EVENTPLAN WHERE Cust_id = ?"
    event_plans = execute_query(query, (customer_id,))
    return jsonify({'recent_event_plans': event_plans}), 200

if __name__ == '__main__':
    app.run(debug=True)
