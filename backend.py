from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import requests, sys
import time as t
import streamlit as st
import pandas as pd
import sqlitecloud
from sqlitecloud import SQLiteCloudError


@st.cache_resource
def get_cloud_connection():
    """Connect to the SQLite Cloud database"""
    db_url = st.secrets["sqlitecloud"]["url"]
    connection = sqlitecloud.connect(db_url)
    connection.execute("CREATE TABLE IF NOT EXISTS apod_table (date TEXT PRIMARY KEY, title TEXT, url TEXT, "
                       "explanation TEXT, media_type TEXT);")
    return connection

def check_cloud_connection():
    """Check if the SQLite cloud database connection is available"""
    try:
        conn.execute("SELECT * FROM apod_table")
        return True
    except SQLiteCloudError:
        return False


load_dotenv()
API_KEY = st.secrets["API_KEY"]
conn = get_cloud_connection()


def daily_api_request():
    """Request APOD data from the API daily and return today's date if data is available"""
    # Uses UTC timezone to fetch data daily
    now_utc = datetime.now(timezone.utc)

    today = now_utc.date()
    if now_utc.hour < 6:
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
    query = "SELECT * FROM apod_table WHERE date = ?;"
    cursor = conn.execute(query, parameters=(str(day),))
    rows = cursor.fetchall()
    cols = [column[0] for column in cursor.description]
    return pd.DataFrame(rows, columns=cols)

def insert_db(content):
    """Insert new APOD data to the local database"""
    # Fetch image data if available
    try:
        image_url = content['url']
    except KeyError:
        image_url = None

    # Insert APOD data into database
    query = "INSERT INTO apod_table (date, title, url, explanation, media_type) VALUES (?, ?, ?, ?, ?)"
    conn.execute(query, parameters=(content['date'], content['title'], image_url,
                         content['explanation'], content['media_type']))

def printall_db():  
    """Print all recorded APOD data from the local database"""
    query = "SELECT * FROM apod_table ORDER BY date DESC"
    data = conn.execute(query)
    print(data)

def cleanup_old_db(days_to_keep=30):
    """Delete records older than the specified number of days"""
    oldest_date = datetime.today().date() - timedelta(days=days_to_keep)
    conn.execute("DELETE FROM apod_table WHERE date < ?", parameters=(str(oldest_date),))

def title_emoji(content):
    """Select an emoji for the given APOD based on its explanation"""
    explanation = content['explanation'].lower()
    words = ["galaxy", "spacecraft",  "star", "moon", "sun", "satellite",]
    emojis  = [":milky_way:", ":rocket:", ":dizzy:", ":crescent_moon:", ":sunny:", ":artificial_satellite:"]

    for i, word in enumerate(words):
        if word in explanation:
            return emojis[i]
    return ":stars:"


if __name__ == '__main__':
    daily_api_request()
    printall_db()
