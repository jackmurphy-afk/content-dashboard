from flask import Flask, redirect, url_for, session, request, render_template, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/yt-analytics.readonly']

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=url_for('oauth2callback', _external=True)
)

@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
    return redirect(url_for('dashboard'))

@app.route('/authorize')
def authorize():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
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
    return jsonify(response['items'][0])

# Add more API routes for data

if __name__ == '__main__':
    app.run(debug=True)