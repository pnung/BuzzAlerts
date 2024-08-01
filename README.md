# BuzzAlerts 🐝

## Overview
BuzzAlerts is a tool designed to help Georgia Tech students track class availability and receive notifications when a spot opens up. The tool utilizes web scraping with Selenium to monitor the registration site and sends email alerts when a seat becomes available.

## Features
- Track multiple classes by CRN (Course Reference Number).
- Receive notifications via email when a seat becomes available.
- Easy to configure and use.
- Completely free!

## Prerequisites
- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver corresponding to your Chrome version
- Gmail account with an app password

## Installation

1. **Clone the Repository**  
   `git clone https://github.com/pnung/BuzzAlerts`  
   `cd BuzzAlerts`

2. **Set Up Virtual Environment**  
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install Dependencies**  
   `pip install -r requirements.txt`

4. **Download ChromeDriver**  
   Download the ChromeDriver that matches your version of Chrome from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and place it in an accessible directory.

5. **Update the Config File**  
   Open the `config.py` file in the project directory and update the following content:
   ```python
   SENDER_EMAIL = 'your-email@gmail.com'
   RECEIVER_EMAIL = 'recipient-email@gmail.com'
   EMAIL_PASSWORD = 'your-app-password'
   CHROME_DRIVER_PATH = '/path/to/chromedriver/executable' # Ensure this is the path to the executable file and not the Chrome Driver folder
   CHROME_BINARY_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' 

   # To find your CHROME_BINARY_PATH:
   # On macOS: Open Finder, navigate to Applications, find Google Chrome, right-click it, select "Show Package Contents", then navigate to Contents/MacOS/Google Chrome.
   # On Windows: Typically, the path will be something like C:\Program Files\Google\Chrome\Application\chrome.exe. You can verify this by right-clicking the Chrome shortcut, selecting "Properties", and checking the "Target" field.
   # On Linux: The path is usually /usr/bin/google-chrome or /usr/bin/chromium-browser.
   
7. **Generate an App Password for Gmail**
   - Follow these steps to generate an app password:
     1. Go to your [Google Account](https://myaccount.google.com/).
     2. Select "Security".
     3. Under "Signing in to Google", select "App passwords".
     4. You might need to sign in again.
     5. At the bottom, choose "Select app" and choose "Other (Custom name)".
     6. Type a name (e.g., "BuzzNotifier") and click "Generate".
     7. Copy the app password and paste it into the `EMAIL_PASSWORD` field in your `config.py`.

## Usage

### Run the Script
`/path/to/venv/bin/python main.py`

### Enter Class Information
The script will prompt you to enter the CRN, subject, and course number for each class you want to track. After entering the details, you will be asked if you want to track another class. Respond with 'y' for yes or 'n' for no.

### Receive Notifications
The script will start monitoring the classes and send an email notification to your specified email address when a spot becomes available.
