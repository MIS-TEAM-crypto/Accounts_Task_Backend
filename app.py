from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Your deployed Apps Script Web App URL (ends with /exec)
GAS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz2TesXQJKGEZNo6yhWPKquODzvb3mz2PZCbQw2-dR8LDxRdDlMPuXWXfanxPXVu5ASmw/exec"

app = Flask(__name__)
CORS(app)  # allow all origins; you can restrict later

def forward_get_to_gas(params):
    """Helper for GET: call Apps Script and always return JSON."""
    r = requests.get(GAS_WEB_APP_URL, params=params)
    print("GET to GAS:", r.url)
    print("GAS status:", r.status_code)
    print("GAS body:", r.text[:500])  # first 500 chars for debugging

    try:
        data = r.json()
    except Exception as e:
        print("JSON decode error:", e)
        # Always return JSON to frontend, even on failure
        data = {"success": False, "error": "Invalid response from Apps Script", "raw": r.text}

    # If Apps Script returned non-2xx, keep that status; otherwise 200
    status = r.status_code if r.status_code >= 400 else 200
    return jsonify(data), status

def forward_post_to_gas(json_payload):
    """Helper for POST: call Apps Script with JSON and always return JSON."""
    r = requests.post(GAS_WEB_APP_URL, json=json_payload)
    print("POST to GAS:", GAS_WEB_APP_URL)
    print("Payload:", json_payload)
    print("GAS status:", r.status_code)
    print("GAS body:", r.text[:500])

    try:
        data = r.json()
    except Exception as e:
        print("JSON decode error:", e)
        data = {"success": False, "error": "Invalid response from Apps Script", "raw": r.text}

    status = r.status_code if r.status_code >= 400 else 200
    return jsonify(data), status

# ---------- USER TASKS ----------
@app.get("/api/user-tasks")
def get_user_tasks():
    username = request.args.get("username", "")
    date = request.args.get("date", "")
    params = {
        "action": "getTasks",
        "username": username,
        "date": date
    }
    return forward_get_to_gas(params)

# ---------- MANAGER TASKS ----------
@app.get("/api/manager-tasks")
def get_manager_tasks():
    manager = request.args.get("manager", "")
    date = request.args.get("date", "")
    params = {
        "action": "getManagerTasks",
        "manager": manager,
        "date": date
    }
    return forward_get_to_gas(params)

# ---------- UPDATE STATUS (Yes/No) ----------
@app.post("/api/update-status")
def update_status():
    payload = request.get_json(force=True, silent=True) or {}
    payload["action"] = "updateStatus"
    return forward_post_to_gas(payload)

# ---------- LEAVE ----------
@app.post("/api/leave")
def leave():
    payload = request.get_json(force=True, silent=True) or {}
    payload["action"] = "leave"
    return forward_post_to_gas(payload)

# ---------- ADMIN: ALL USER STATUSES ----------
@app.get("/api/all-status")
def get_all_status():
    date = request.args.get("date", "")
    manager = request.args.get("manager", "")
    username = request.args.get("username", "")

    params = {
        "action": "getAllStatus",
        "date": date,
        "manager": manager,
        "username": username
    }

    return forward_get_to_gas(params)

@app.get("/api/all-status-range")
def get_all_status_range():
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    username = request.args.get("username", "")  # optional, Apps Script handles empty

    params = {
        "action": "getStatusRange",
        "start": start,
        "end": end,
        "username": username
    }
    return forward_get_to_gas(params)

# ---------- NEW ROUTES FOR ASSIGN FEATURE ----------

@app.get("/api/user-team")
def api_user_team():
    """
    Returns list of usernames for Assign dropdown.
    (Logic of who is in the team is in Apps Script getUserTeam_().)
    """
    username = request.args.get("username", "")
    params = {
        "action": "getUserTeam",
        "username": username,
    }
    return forward_get_to_gas(params)


@app.post("/api/assign-task")
def api_assign_task():
    """
    Assign a task from one user to another for a specific date.
    """
    data = request.get_json(force=True) or {}
    payload = {
        "action": "assignTask",
        "username": data.get("username", ""),   # who is assigning away
        "task": data.get("task", ""),
        "manager": data.get("manager", ""),
        "date": data.get("date", ""),
        "assignTo": data.get("assignTo", ""),   # assignee
    }
    return forward_post_to_gas(payload)


if __name__ == "__main__":
    app.run(debug=True)
