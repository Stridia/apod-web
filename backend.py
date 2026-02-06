from dotenv import load_dotenv
import requests, os
from streamlit import connection
from sqlalchemy import text
from datetime import date, timedelta

load_dotenv()
API_KEY = os.getenv("API_KEY")
conn = connection('apod_db', type='sql')

def get_apod_data(day):
    """Get and return the APOD data (either from API or database) on a certain date"""
    # Fetch APOD data straight from the database
    data = fetch_db(day)
    if not data.empty:
        content = data.iloc[0].to_dict()
    else:
        try:
            # Request APOD data from NASA's API (If not present in database) and insert it to the database
            content = request_api(day)

            # Return None if there's an error when fetching data from the API
            if not content: return None
            insert_db(content)
        except KeyError:
            # Fetch yesterday's data if today's data is not available
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            content = get_apod_data(yesterday)
    return content

def request_api(day):
    """Request APOD data on a certain date from NASA's API"""
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={day}"
    response = requests.get(url)
    if response.status_code == 200: return None
    return response.json()

def fetch_db(day):
    """Fetch APOD data on a certain date from the local database using query"""
    query = "SELECT * FROM apod_table WHERE date = :date;"
    data = conn.query(query, params={'date': day}, ttl=0)
    return data

def insert_db(content):
    """Insert new APOD data to the local database"""
    with conn.session as s:
        s.execute(text("CREATE TABLE IF NOT EXISTS apod_table (date TEXT, title TEXT, url TEXT, explanation TEXT);"))
        s.execute(text("INSERT INTO apod_table VALUES (:date, :title, :url, :explanation);"),
                  params={'date': content['date'], 'title': content['title'],
                          'url': content['url'], 'explanation': content['explanation']})
        s.commit()

def printall_db():
    """Print all recorded APOD data in the local database"""
    data = conn.query("SELECT * FROM apod_table ORDER BY date DESC", ttl=0)
    print(data)

def delete_db(day):
    """Delete APOD data from the local database"""
    with conn.session as s:
        s.execute(text("DELETE FROM apod_table WHERE date = :day"), params={'day': day})
        s.commit()


if __name__ == '__main__':
    printall_db()