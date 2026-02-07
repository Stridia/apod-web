from dotenv import load_dotenv
import requests, os, sys
import time as t
import streamlit as st
from sqlalchemy import text
from datetime import datetime, timedelta

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
    today = datetime.today()
    data = fetch_db(today.date())

    if today.hour >= 12 and data.empty:
        content = request_api(today.date())
        insert_db(content)
        # Cleanup data older than 30 days
        cleanup_old_db()

    if today.hour >= 12:
        return today.date()
    else:
        return today.date() - timedelta(days=1)

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
    """Request APOD data on a certain date from NASA's API"""
    container = st.empty()
    with container.container():
        with st.status(label="Fetching today's wonders from NASA...", expanded=False) as status:
            url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={day}"
            response = requests.get(url)
            status.update(label="Data synced with database!", state="complete")

    t.sleep(1)
    container.empty()
    if response.status_code == 200: return response.json()

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


if __name__ == '__main__':
    printall_db()