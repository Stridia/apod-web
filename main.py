# Astronomy Picture of the Day
import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Get the API Key from .env file
load_dotenv()
api_key = os.getenv("API_KEY")

URL = "https://api.nasa.gov/planetary/apod?" \
      f"api_key={api_key}"
response = requests.get(URL)
content = response.json()

# Web Development
st.subheader("Astronomy Picture of The Day")
st.title(content['title'])
st.image(content['url'])
st.write(content['explanation'])