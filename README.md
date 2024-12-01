
# ChronoKeeper: AI-Powered Appointment Scheduler

ChronoKeeper is an advanced scheduling tool that leverages AI (Cohere API) and Google Calendar integration to streamline appointment management. This README is divided into two main sections: functionality provided by the main script and additional support for Google Calendar integration.

---

## Section 1: Main File (AI-Powered Scheduling)

### Overview

The main script of ChronoKeeper provides AI-powered scheduling using the Cohere API. It defines schedules over a two-week period and intelligently manages appointments.

### Features

- **Customizable Schedules**:
  - Appointments are scheduled within two weeks (`Monday Week1` to `Friday Week2`).
  - Working hours are set from 9:00 AM to 5:00 PM, in 30-minute increments.

- **Appointment Information**:
  - Each appointment requires the following details:
    - **Day**: Day of the week (e.g., `Monday Week1`).
    - **Start Time**: The start time in HH:MM format.
    - **Duration**: Duration in hours (supports fractional values, e.g., 1.5).
    - **Recurrence**: Whether the event recurs (e.g., `weekly`).
    - **Description**: A brief description of the appointment.

- **Cohere API Integration**:
  - Utilizes Cohere to process and categorize appointment descriptions.

- **CSV Parsing**:
  - Appointments can be loaded from a CSV file with the following columns:
    - `day`, `start_time`, `duration`, `description`, `recurrence`

### Example CSV Entry

```csv
Monday Week1,09:00,1,Team meeting,weekly
```

### Running the Main Script

1. Add your Cohere API key in the `main.py` file by replacing the placeholder.
2. Run the script:
   ```bash
   python main.py
   ```

---

## Section 2: Google Calendar Support

### Overview

ChronoKeeper integrates with Google Calendar to automatically add and manage events. This functionality requires setting up OAuth credentials and enabling the Google Calendar API.

### Setting Up Google Calendar Integration

1. **Obtain OAuth Credentials**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
   - Navigate to **APIs & Services** > **Credentials**.
   - Click **Create Credentials** > **OAuth 2.0 Client IDs**.
     - Choose **Desktop App** as the application type.
   - Download the `.json` file containing your client credentials.

2. **Rename and Place the File**:
   - Rename the downloaded file to `credentials.json`.
   - Place the renamed file in the root directory of the ChronoKeeper project.

3. **Token Generation**:
   - On the first run, the application will prompt you to authenticate with Google via your browser.
   - After successful authentication, a `token.json` file will be automatically generated and saved in the project root.

4. **DevContainer Configuration**:
   - If running in a development container, forward port **5555** from the container to the host machine. This is required for the OAuth flow to complete successfully.

### Running the Google Calendar Integration Script

1. Ensure `credentials.json` is in the project root.
2. Add your calendar ID to `calendar_id.txt`.
3. Run the script to upload appointments from a CSV to Google Calendar:
   ```bash
   python write_csv_to_google_celendar.py
   ```

### File Overview for Google Calendar Support

- **`write_csv_to_google_celendar.py`**:
  - Reads appointments from a CSV file and adds them to Google Calendar.
- **`calendar_id.txt`**:
  - Stores the Google Calendar ID used for event creation.
- **`credentials.json`**:
  - Contains your Google OAuth credentials (user-provided).
- **`token.json`**:
  - Automatically generated session token for Google OAuth.

---

## Additional Notes

- **Security**:
  - Never share `credentials.json` or `token.json` files publicly.
- **Customization**:
  - Adjust working hours or days in `main.py` as needed.
