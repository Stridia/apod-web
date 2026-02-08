from dotenv import load_dotenv
import requests, os, sys
import time as t
import streamlit as st
from sqlalchemy import text
from datetime import datetime, timedelta, timezone

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Database Connection
conn = st.connection('apod_db', type='sql')
with conn.session as s:
    s.execute(text("CREATE TABLE IF NOT EXISTS apod_table (date TEXT, title TEXT, url TEXT, "
                   "explanation TEXT, media_type TEXT);"))
    s.commit()


def daily_api_request():
    """Request APOD data from the API daily and return today's date if data is available"""
    # Uses UTC timezone to fetch data daily
    now_utc = datetime.now(timezone.utc)

    today = now_utc.date()
    if now_utc.hour < 5:
        today = today - timedelta(days=1)

    data = fetch_db(today)
    if data.empty:
        content = request_api(today)
        insert_db(content)
        cleanup_old_db(30)

    return today

def get_apod_data(day):
    """Get and return the APOD data (either from API or database) on a certain date"""
    # Fetch APOD data straight from the database
    data = fetch_db(day)
    if not data.empty:
        content = data.iloc[0].to_dict()
    else:
        # Request APOD data from NASA's API (If not present in database) and insert it to the database
        content = request_api(day)
        insert_db(content)
    return content

def request_api(day):
    """Request APOD data on a certain date from NASA's API
       Additionally, add supporting emojis in the beginning of APOD titles"""
    container = st.empty()
    with container.container():
        with st.status(label="Fetching today's wonders from NASA...", expanded=False) as status:
            url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={day}"
            response = requests.get(url)
            status.update(label="Data synced with database!", state="complete")

    t.sleep(1)
    container.empty()

    if response.status_code == 200:
        content = response.json()

        # Select an emoji for each APOD data
        content['title'] = title_emoji(content) + ' ' + content['title']

        return content

    # Display error message if there's trouble fetching data from the API
    st.text("Sorry, NASA's servers may currently be down today due to "
            "unprecedented alien invasions. Check again later!")
    sys.exit(0)

def fetch_db(day):
    """Fetch APOD data on a certain date from the local database using query"""
    query = "SELECT * FROM apod_table WHERE date = :date;"
    data = conn.query(query, params={'date': day}, ttl=0)
    return data

def insert_db(content):
    """Insert new APOD data to the local database"""
    # Fetch image data if available
    try:
        image_url = content['url']
    except KeyError:
        image_url = None

    # Insert APOD data into database
    with conn.session as s:
        s.execute(text("INSERT INTO apod_table VALUES (:date, :title, :url, :explanation, :media_type);"),
                  params={'date': content['date'], 'title': content['title'], 'url': image_url,
                          'explanation': content['explanation'], 'media_type': content['media_type']})
        s.commit()

def printall_db():
    """Print all recorded APOD data from the local database"""
    data = conn.query("SELECT * FROM apod_table ORDER BY date DESC", ttl=0)
    print(data)

def cleanup_old_db(days_to_keep=30):
    """Delete records older than the specified number of days"""
    oldest_date = datetime.today().date() - timedelta(days=days_to_keep)
    with conn.session as s:
        s.execute(text("DELETE FROM apod_table WHERE date < :date"), params={'date': oldest_date})
        s.commit()

def title_emoji(content):
    """Select an emoji for the given APOD based on its explanation"""
    explanation = content['explanation'].lower()
    words = ["galaxy", "spacecraft", "satellite", "star", "moon", "sun"]
    emojis  = [":milky_way:", ":rocket:", ":artificial_satellite:", ":dizzy:", ":crescent_moon:", ":sunny:"]

    for i, word in enumerate(words):
        if word in explanation:
            return emojis[i]
    return ":stars:"


if __name__ == '__main__':
    daily_api_request()
    printall_db()
