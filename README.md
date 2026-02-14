# 🌌 NASA's Astronomy Picture of the Day (APOD)

### ✨ https://astronomy-pictures.streamlit.app/ ✨

### A Web Application built with Streamlit that fetches and archives NASA's daily astronomy photography and documentation.

This project is a simple passion project that was built along with [Ardit Sulce's popular Python Mega Course in Udemy](https://www.udemy.com/course/the-python-mega-course/) 
showing how to build a web application using Streamlit and work with APIs. Through an example of working and fetching data from NASA's API,
I further developed the project by adding unique features that improved user experience to hone my web development skills 
as an aspiring software developer.

## 📡 Prominent Features 
### Database Management

   The application is integrated with **SQLite Cloud** database to ensure that collected data is preserved and accessible
   across different devices and other deployment methods.

### Daily Information Update
   
   The application requests and fetches APOD data from NASA's API daily at 06:00 AM UTC and synchronizes with the cloud
   database to ensure data availability and prevent API connection errors.


### Dual-Layer Data Fetching
   
   In order to minimize external API calls and improve load times, the application implements a "Database-First" strategy.
   It prioritizes fetching astronomical data from the cloud cache database before doing an API request when data is
   unavailable in the cloud.

### Rolling Window Storage

   The application features a dynamic and interactive calendar input with a 30-days restriction and an automatic cleanup
   routine in the database that purges records older than those 30 days to maintain storage availability and database performance.
   

## 🛠️ Tech Stack
* Frontend: Streamlit (Python-based web framework)
* Database: SQLite Cloud (Remote persistent storage).
* API: NASA Open APIs (APOD).

## 🚀 BIY (Build It Yourself!)
1. **Prerequisites**

   * IDE (VS Code, PyCharm, etc.)
   * Python 3.11+
   * NASA API Key ([Get yours here!](https://api.nasa.gov/))
   * SQLite Cloud Account ([Sign up here!](https://www.sqlite.ai/))


2. **Clone Repository**

    Clone my repository using Git in your local folder by typing this in your Git Bash:
    ```
    git init
    git clone https://github.com/Stridia/apod-web
    ```
   
3. **Installation**

   After setting up Python's virtual environment (.venv), install the package requirements 
   by typing this in your IDE's terminal:
   ```
   pip install -r requirements.txt
   ```
   
4. **API and Database Configuration**
   * Generate your own NASA API key by signing up on NASA's website
   * Create a new project in SQLite Cloud. In that project, create a new `apod.db` database 
   * Create `.streamlit/secrets.toml` in your project and configure the file as shown in the `secrets.toml.example` file:
   ```toml
   API_KEY="<your-nasa-api-key>"
   
   [sqlitecloud]
   url = "sqlitecloud://<project-id>.sqlite.cloud:<host-port>/apod.db?apikey=<your-db-api-key>"
   ```

5. **Running the App**
   
   After everything's done correctly, run the app by typing this in your IDE's terminal:
   ```terminaloutput
   streamlit run main.py
   ```

🤗🎉 **Happy Coding!**

## ☕ Contributing

Personally, this is a very simple passion project and I don't think I will be further updating it other than maybe doing
a few tweaks / bug fixes here and there. However, if you have an idea for a really cool feature on this project, **feel free
to fork this project and open a PR or develop it on your own projects!** Who knows, perhaps I'd be interested in making this
a full-fledged interactive web application!

🤗 Either way, thank you for stopping by and checking out my project!
