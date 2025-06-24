from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth

# Create Flask app instance
app = Flask(__name__)
# Initialize HTTP Basic Auth for the app
auth = HTTPBasicAuth()

# In-memory user credentials for authentication
USERS = {
    "user": "pass"
}

# In-memory environment variables (simulate a central config)
ENV_VARS = {
    "DB_HOST": "db.local",
    "REDIS_URL": "redis://redis:6379/0",
    "SECRET_KEY": "verysecret"
}

@auth.verify_password
def verify_password(username, password):
    """
    Verify user credentials for HTTP Basic Auth.
    """
    return USERS.get(username) == password

@app.route('/env', methods=['GET'])
@auth.login_required
def get_env():
    """
    GET endpoint to return requested environment variables as JSON.
    The variable names are passed via 'vars' query parameter (comma-separated).
    """
    vars_param = request.args.get('vars', '')
    keys = vars_param.split(',')
    return jsonify({k: ENV_VARS[k] for k in keys if k in ENV_VARS})

@app.route('/env', methods=['POST'])
@auth.login_required
def update_env():
    """
    POST endpoint to update environment variables at runtime.
    Accepts a JSON body with key-value pairs.
    """
    data = request.json
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data"}), 400
    ENV_VARS.update(data)
    return jsonify({"updated": list(data.keys())}), 200

if __name__ == "__main__":
    # Start Flask server on all interfaces, port 8000
    app.run(host='0.0.0.0', port=8000)
