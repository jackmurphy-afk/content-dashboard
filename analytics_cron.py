import os
import requests
from supabase import create_client, Client
from datetime import datetime
import schedule
import time

# Load environment variables
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def fetch_youtube_videos():
    # Get 25 most recent videos
    search_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={YOUTUBE_CHANNEL_ID}&order=date&maxResults=25&key={YOUTUBE_API_KEY}'
    search_response = requests.get(search_url)
    search_data = search_response.json()
    
    if 'items' not in search_data:
        print("Error fetching videos:", search_data)
        return
    
    video_ids = [item['id']['videoId'] for item in search_data['items'] if item['id']['kind'] == 'youtube#video']
    
    # Get statistics for videos
    stats_url = f'https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={",".join(video_ids)}&key={YOUTUBE_API_KEY}'
    stats_response = requests.get(stats_url)
    stats_data = stats_response.json()
    
    if 'items' not in stats_data:
        print("Error fetching stats:", stats_data)
        return
    
    records = []
    for item in stats_data['items']:
        video_id = item['id']
        snippet = item['snippet']
        stats = item['statistics']
        
        title = snippet['title']
        thumbnail_url = snippet['thumbnails'].get('high', {}).get('url', '')
        published_at = snippet['publishedAt']
        
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        
        # YouTube Data API does not provide shares, saves, reach, watch time directly
        shares = None
        saves = None
        reach = None
        watch_time = None  # Not available in Data API v3
        
        # Calculate engagement rate (likes + comments) / views * 100
        engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
        
        record = {
            'platform': 'youtube',
            'post_id': video_id,
            'title': title,
            'thumbnail_url': thumbnail_url,
            'published_at': published_at,
            'views': views,
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'saves': saves,
            'reach': reach,
            'engagement_rate': engagement_rate
        }
        records.append(record)
    
    # Upsert records
    supabase.table('content_analytics').upsert(records, on_conflict='post_id')
    print(f"Upserted {len(records)} YouTube video records")

def run_job():
    fetch_youtube_videos()

# Schedule to run every 6 hours
schedule.every(6).hours.do(run_job)

# Run immediately on start
run_job()

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute