from __future__ import print_function
import os
import csv
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the token.json file
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID_FILE = "calendar_id.txt"  # File to read the calendar ID from

def get_monday_of_current_week():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())  # Subtract days to get to Monday
    return monday

def parse_schedule(csv_file):
    schedule = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Parse day, time, duration, and description
            day, start_time, duration, description, reoccurrence = row.values()
            duration = float(duration)
            event_start = None

            # Determine the date based on the "Day" field
            if "Week1" in day:
                week_offset = 0
            elif "Week2" in day:
                week_offset = 1
            else:
                continue

            # Get the specific weekday
            weekday = day.split()[0]
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekday_index = weekdays.index(weekday)

            monday_of_week = get_monday_of_current_week() + timedelta(weeks=week_offset)
            event_start = monday_of_week + timedelta(days=weekday_index)
            
            # Combine date with time
            event_start = datetime.combine(event_start, datetime.strptime(start_time, "%H:%M").time())
            event_end = event_start + timedelta(hours=duration)
            
            # Add to schedule
            schedule.append({
                "start": event_start,
                "end": event_end,
                "description": description
            })
    return schedule

def get_calendar_id():
    if os.path.exists(CALENDAR_ID_FILE):
        with open(CALENDAR_ID_FILE, 'r') as file:
            calendar_id = file.read().strip()
            if calendar_id:
                print(f"Using calendar ID from file: {calendar_id}")
                return calendar_id
    print("No calendar ID found in file. Using primary calendar.")
    return 'primary'

def add_events_to_calendar(service, events, calendar_id):
    for event in events:
        event_body = {
            "summary": event["description"],
            "start": {"dateTime": event["start"].isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": event["end"].isoformat(), "timeZone": "UTC"}
        }
        created_event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        print(f"Event created: {created_event['summary']} on {created_event['start']['dateTime']}")

def main():
    creds = None
    # The token.json file stores the user's access and refresh tokens, created automatically.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials available, log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=5555)
        # Save credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Connect to the Google Calendar API
    service = build('calendar', 'v3', credentials=creds)

    # Get calendar ID (default to primary if not specified)
    calendar_id = get_calendar_id()
    
    # Parse schedule and add events
    schedule = parse_schedule('notadatabase.csv') 
    add_events_to_calendar(service, schedule, calendar_id)

if __name__ == '__main__':
    main()
