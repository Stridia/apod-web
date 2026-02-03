# Astronomy Picture of the Day
import streamlit as st
from datetime import date, timedelta
from sqlalchemy import text
from dotenv import load_dotenv
import requests
import os

load_dotenv()
api_key = os.getenv("API_KEY")
today = date.today().isoformat()

# Connect with SQL Database
conn = st.connection('apod_db', type='sql')
query = "SELECT * FROM apod_table WHERE date = :today;"
data = conn.query(query, params={'today': today}, ttl=0)

if not data.empty:
    # Fetch the data straight from the database
    content = data.iloc[0].to_dict()
else:
    try:
        # Request today's APOD data from NASA's API
        url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&date={today}"
        response = requests.get(url)
        content = response.json()

        # Update the database with today's APOD
        with conn.session as s:
            s.execute(text("CREATE TABLE IF NOT EXISTS apod_table (date TEXT, title TEXT, url TEXT, explanation TEXT);"))
            s.execute(text("INSERT INTO apod_table VALUES (:date, :title, :url, :explanation);"),
                      params={'date': today, 'title': content['title'],
                              'url': content['url'], 'explanation': content['explanation']})
            s.commit()
    except KeyError:
        # Fetch yesterday's data if today's data is not available
        query = "SELECT * FROM apod_table WHERE date = :yesterday;"
        data = conn.query(query, params={'yesterday': date.today() - timedelta(days=1)}, ttl=0)
        content = data.iloc[0].to_dict()


# Web Development
st.title(content['title'])
st.subheader("Astronomy Picture of The Day")
st.text(content['date'])
st.image(content['url'])
st.write(content['explanation'])
