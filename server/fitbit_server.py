from flask import Flask, redirect, request, render_template_string, jsonify
import requests
import base64
import urllib.parse
from datetime import datetime
import time
import threading

app = Flask(__name__)

# Replace with your values from Fitbit Developer Portal
CLIENT_ID = "23QH3K"
CLIENT_SECRET = "c6ef10009a62aee25a4bc349b43ac443"
REDIRECT_URI = "http://127.0.0.1:8000/callback"

# Global variables to store tokens and data
access_token = None
refresh_token = None
heart_rate_data = []
is_monitoring = False

def refresh_access_token():
    """Refresh the access token using the refresh token"""
    global access_token, refresh_token
    
    if not refresh_token:
        return False
    
    token_url = "https://api.fitbit.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    basic_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens["access_token"]
            refresh_token = tokens.get("refresh_token", refresh_token)  # Keep old refresh token if new one not provided
            print(f"✅ Token refreshed successfully at {datetime.now()}")
            return True
        else:
            print(f"❌ Token refresh failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        return False

def fetch_heart_rate_data():
    """Fetch heart rate data from Fitbit API"""
    global access_token, heart_rate_data
    
    if not access_token:
        print("❌ No access token available")
        return False
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        intraday_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{today}/1d/1sec.json"
        
        response = requests.get(intraday_url, headers={"Authorization": f"Bearer {access_token}"})
        
        if response.status_code == 401:
            # Token expired, try to refresh
            print("🔄 Token expired, attempting refresh...")
            if refresh_access_token():
                # Retry with new token
                response = requests.get(intraday_url, headers={"Authorization": f"Bearer {access_token}"})
            else:
                return False
        
        if response.status_code == 200:
            data = response.json()
            values = data.get("activities-heart-intraday", {}).get("dataset", [])
            
            if values:
                latest = values[-1]
                heart_rate_data.append({
                    'timestamp': datetime.now().isoformat(),
                    'heart_rate': latest.get('value'),
                    'time': latest.get('time')
                })
                print(f"🫀 Heart Rate: {latest.get('value')} BPM at {latest.get('time')}")
                return True
            else:
                print("📊 No heart rate data available")
                return False
        else:
            print(f"❌ Error fetching heart rate: {response.status_code} {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in fetch_heart_rate_data: {e}")
        return False

def continuous_monitoring():
    """Continuous heart rate monitoring loop"""
    global is_monitoring
    
    while is_monitoring:
        fetch_heart_rate_data()
        time.sleep(60)  # Fetch every minute

@app.route('/')
def home():
    scope = "heartrate activity profile"
    url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&scope={urllib.parse.quote(scope)}"
    return redirect(url)

@app.route('/callback')
def callback():
    global access_token, refresh_token
    
    code = request.args.get("code")
    if not code:
        return """
        <h2>❌ No authorization code received</h2>
        <p>Please go back to <a href="/">the home page</a> and try again.</p>
        <p><strong>Note:</strong> Authorization codes expire quickly and can only be used once.</p>
        """

    # Exchange code for tokens
    token_url = "https://api.fitbit.com/oauth2/token"
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    basic_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    token_resp = requests.post(token_url, headers=headers, data=data)
    if token_resp.status_code != 200:
        error_msg = token_resp.text
        return f"""
        <h2>❌ Token Error</h2>
        <p><strong>Error:</strong> {error_msg}</p>
        <p><strong>Solution:</strong></p>
        <ul>
            <li>Clear your browser cache/cookies for Fitbit</li>
            <li>Or use an incognito/private window</li>
            <li>Go back to <a href="/">the home page</a> and try again</li>
        </ul>
        <p><strong>Note:</strong> Authorization codes expire quickly and can only be used once.</p>
        """

    tokens = token_resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token")

    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Now fetch intraday heart-rate data with correct date format
    intraday_url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{today}/1d/1sec.json"
    hr_resp = requests.get(intraday_url,
                           headers={"Authorization": f"Bearer {access_token}"})
    if hr_resp.status_code != 200:
        return f"""
        <h2>❌ Heart Rate Data Error</h2>
        <p><strong>Error:</strong> {hr_resp.status_code} {hr_resp.text}</p>
        <p>✅ <strong>Access Token:</strong> <code>{access_token}</code></p>
        <p>🔄 <strong>Refresh Token:</strong> <code>{refresh_token}</code></p>
        <p>You can use these tokens in your Flutter app.</p>
        """

    hr_data = hr_resp.json()
    values = hr_data.get("activities-heart-intraday", {}).get("dataset", [])
    latest = values[-1] if values else None
    output = f"Latest HR reading: {latest}" if latest else "No data found."

    return f"""
      <h2>✅ Success!</h2>
      <p><strong>Access Token:</strong> <code>{access_token}</code></p>
      <p><strong>Refresh Token:</strong> <code>{refresh_token}</code></p>
      <p><strong>🫀 Heart Rate:</strong> {output}</p>
      <p><strong>📊 Data Points:</strong> {len(values)} points</p>
      <p><strong>📅 Date:</strong> {today}</p>
      <hr>
      <p><strong>API Endpoints:</strong></p>
      <ul>
        <li><a href="/start_monitoring">Start Continuous Monitoring</a></li>
        <li><a href="/stop_monitoring">Stop Monitoring</a></li>
        <li><a href="/get_data">Get Latest Data</a></li>
        <li><a href="/refresh_token">Refresh Token</a></li>
      </ul>
      <hr>
      <p><strong>Next Steps:</strong></p>
      <ol>
        <li>Copy the tokens above</li>
        <li>Use the API endpoints to monitor heart rate continuously</li>
        <li>Update your Flutter app with these tokens</li>
      </ol>
    """

@app.route('/start_monitoring')
def start_monitoring():
    global is_monitoring
    
    if not access_token:
        return jsonify({"error": "No access token available. Please authenticate first."})
    
    if is_monitoring:
        return jsonify({"message": "Monitoring is already running"})
    
    is_monitoring = True
    # Start monitoring in a separate thread
    monitor_thread = threading.Thread(target=continuous_monitoring, daemon=True)
    monitor_thread.start()
    
    return jsonify({
        "message": "Continuous monitoring started",
        "status": "running",
        "fetch_interval": "60 seconds"
    })

@app.route('/stop_monitoring')
def stop_monitoring():
    global is_monitoring
    is_monitoring = False
    return jsonify({
        "message": "Monitoring stopped",
        "status": "stopped"
    })

@app.route('/get_data')
def get_data():
    return jsonify({
        "heart_rate_data": heart_rate_data,
        "total_readings": len(heart_rate_data),
        "latest_reading": heart_rate_data[-1] if heart_rate_data else None
    })

@app.route('/refresh_token')
def refresh_token_endpoint():
    if refresh_access_token():
        return jsonify({
            "message": "Token refreshed successfully",
            "access_token": access_token[:20] + "..." if access_token else None
        })
    else:
        return jsonify({"error": "Failed to refresh token"})

if __name__ == '__main__':
    app.run(port=8000, debug=True)
