# Social Media Analytics Cron Job and Dashboard

This project includes a cron job script for fetching YouTube analytics and storing in Supabase, and a web dashboard for visualizing the data with Jane App's design system.

## Dashboard Features

- **Controls**: Format filter buttons (All, Videos, Shorts), time range buttons (7d, 28d, 90d, 365d, Custom), sort dropdown for top content.
- **KPI Cards**: 6 cards with sparklines and percentage changes.
- **Charts**: Views & Impressions area chart, Engagement Breakdown bar chart.
- **Top Performing Content**: Sortable grid with format filtering.
- **Video Deep Dive**: Lookup with channel averages.
- **Traffic Sources & Geography**: Horizontal bar charts.
- **Styling**: Jane App brand colors (#00C1CA primary, etc.), clean typography, responsive design.

## Cron Job Setup

...

## Dashboard Setup

1. Set up Google Cloud Console:
   - Create a project
   - Enable YouTube Data API v3 and YouTube Analytics API
   - Create OAuth 2.0 credentials (Web application)
   - Download client_secret.json and place in the project root

2. Set environment variables in `.env`:
   - `GOOGLE_CLIENT_ID`: From client_secret.json
   - `GOOGLE_CLIENT_SECRET`: From client_secret.json

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the dashboard:
   ```
   python app.py
   ```

5. Open http://localhost:5000 in your browser and authorize with Google.

## Notes

- The dashboard uses OAuth for YouTube APIs.
- Controls filter all sections dynamically.
- Full data fetching requires implementing API routes in `app.py`.