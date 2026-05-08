from flask import Flask, redirect, url_for, session, request, render_template, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# OAuth configuration from environment variables
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/yt-analytics.readonly']
    
    flow = Flow.from_client_config(
        {
            "installed": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:5000/oauth2callback", os.getenv('VERCEL_URL', 'http://localhost:5000') + '/oauth2callback']
            }
        },
        scopes=SCOPES,
        redirect_uri=os.getenv('VERCEL_URL', 'http://localhost:5000') + '/oauth2callback'
    )
else:
    flow = None

@app.route('/')
def index():
    if not flow:
        return jsonify({"error": "OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."}), 500
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
    return redirect(url_for('dashboard'))

@app.route('/authorize')
def authorize():
    if not flow:
        return jsonify({"error": "OAuth not configured"}), 500
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    if not flow:
        return jsonify({"error": "OAuth not configured"}), 500
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect(url_for('dashboard'))

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_credentials():
    creds_dict = session.get('credentials')
    if not creds_dict:
        return None
    return Credentials(**creds_dict)

@app.route('/dashboard')
def dashboard():
    creds = get_credentials()
    if not creds:
        return redirect(url_for('authorize'))
    return render_template('dashboard.html')

@app.route('/api/channel_info')
def api_channel_info():
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    youtube = build('youtube', 'v3', credentials=creds)
    channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
    response = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    ).execute()
    if response['items']:
        return jsonify(response['items'][0])
    return jsonify({'error': 'Channel not found'}), 404

# Add more API routes for data

if __name__ == '__main__':
    app.run(debug=False)