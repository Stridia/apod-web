import streamlit as st
import backend as b
from datetime import date, timedelta

# Connect with SQL Database
conn = st.connection('apod_db', type='sql')
today = date.today().isoformat()
data = b.fetch_db(conn, today)

if not data.empty:
    # Fetch APOD data straight from the database
    content = data.iloc[0].to_dict()
else:
    try:
        # Request today's APOD data from NASA's API
        content = b.request_api(today)

        # Insert today's APOD data to the database
        b.insert_db(conn, content)
    except KeyError:
        # Fetch yesterday's data if today's data is not available
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        data = b.fetch_db(conn, yesterday)
        content = data.iloc[0].to_dict()


# Web Development
st.title(content['title'])
st.subheader("Astronomy Picture of The Day")
st.text(content['date'])
st.image(content['url'])
st.write(content['explanation'])
