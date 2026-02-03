from dotenv import load_dotenv
import requests, os
import streamlit as st
from sqlalchemy import text

load_dotenv()
API_KEY = os.getenv("API_KEY")


def request_api(day):
    """Request APOD data on a certain date from NASA's API"""
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={day}"
    response = requests.get(url)
    return response.json()

def fetch_db(connection, day):
    """Fetch APOD data on a certain date from the local database using query"""
    query = "SELECT * FROM apod_table WHERE date = :date;"
    data = connection.query(query, params={'date': day}, ttl=0)
    return data

def insert_db(connection, content):
    """Insert new APOD data to the local database"""
    with connection.session as s:
        s.execute(text("CREATE TABLE IF NOT EXISTS apod_table (date TEXT, title TEXT, url TEXT, explanation TEXT);"))
        s.execute(text("INSERT INTO apod_table VALUES (:date, :title, :url, :explanation);"),
                  params={'date': content['date'], 'title': content['title'],
                          'url': content['url'], 'explanation': content['explanation']})
        s.commit()

def printall_db(connection):
    """Print all recorded APOD data in the local database"""
    data = connection.query("SELECT * FROM apod_table ORDER BY date DESC", ttl=0)
    print(data)

def delete_db(connection, day):
    """Delete APOD data from the local database"""
    with connection.session as s:
        s.execute(text("DELETE FROM apod_table WHERE date = :day"), params={'day': day})
        s.commit()


if __name__ == '__main__':
    conn = st.connection('apod_db', type='sql')
    printall_db(conn)