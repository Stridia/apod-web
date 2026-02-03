import streamlit as st
import backend as b
from datetime import date, timedelta

# Connect with SQL Database
conn = st.connection('apod_db', type='sql')
today = date.today()

# Date Input
st.subheader("Astronomy Picture of The Day")
day = st.date_input("", today, label_visibility="collapsed", format="DD.MM.YYYY",
                    max_value=today, min_value=today - timedelta(days=30))

# Fetch APOD data straight from the database
data = b.fetch_db(conn, day)
if not data.empty:
    content = data.iloc[0].to_dict()
else:
    try:
        # Request APOD data from NASA's API (If not present in database) and insert it to the database
        content = b.request_api(day)
        b.insert_db(conn, content)
    except KeyError:
        # Fetch yesterday's data if today's data is not available
        yesterday = (today - timedelta(days=1)).isoformat()
        data = b.fetch_db(conn, yesterday)
        content = data.iloc[0].to_dict()

# Change date format (Ex: 2026-02-01 -> Sunday, 01 February 2026)
content['date'] = date.strptime(content['date'], '%Y-%m-%d').strftime('%A, %d %B %Y')

# Show APOD (Web Development)
st.title(content['title'])
st.write(content['date'])
st.image(content['url'])
st.write(content['explanation'])
