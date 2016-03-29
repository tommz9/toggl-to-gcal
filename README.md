# toggl-to-gcal
A simple script for uploading Toggl entries into a Google calendar.

## Requirements

- Python 3
- Toggl account
  - you need the API token from My Profile 
- Google account
- Google calendar
  - you need to get Calendar Address of the calendar from the settings of the calendar
- Google project with OAuth 2.0 client ID
  - https://developers.google.com/google-apps/calendar/quickstart/python#prerequisites
  - you need the client_secret.json file

1. Set the timezone in toggl-to-gcal.py
2. Enter the Toggl token and Calendar address
3. Cope the client_secret.json file to the folder with the script
4. run python3 toggl-to-gcal.py YYYY-MM-DD to copy the entriens from Toggl to Google Calendar
