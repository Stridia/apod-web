import streamlit as st
from datetime import date, timedelta
from backend import get_apod_data

st.set_page_config(page_title="Astronomy Picture of The Day", layout="wide")

# Connect with SQL Database
conn = st.connection('apod_db', type='sql')
today = date.today()

# Date Input
st.subheader("Astronomy Picture of The Day")
day = st.date_input("", today, label_visibility="collapsed", format="DD.MM.YYYY",
                    max_value=today, min_value=today - timedelta(days=30))

# Get the APOD data
content = get_apod_data(day)

# Change date format (Ex: 2026-02-01 -> Sunday, 01 February 2026)
content['date'] = date.strptime(content['date'], '%Y-%m-%d').strftime('%A, %d %B %Y')

# Web Development
if content:
    col1, col2 = st.columns([0.4, 0.6], width=2000)

    with col1:
        st.image(content['url'])

    with col2:
        st.title(content['title'])
        st.write(content['date'])
        st.write(content['explanation'])
else:
    st.text("Sorry, NASA's servers may currently be down today due to uprecedented alien invasions. Check again later!")
