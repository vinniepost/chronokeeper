import pandas as pd

# Load the notadatabase.csv file
not_a_database = pd.read_csv('notadatabase.csv')
not_a_database['time'] = pd.to_datetime(not_a_database['time'])  # Ensure the time column is in datetime format

# Define the column names and time variables
header = not_a_database.columns  # id, time, duration, plan, company, frequency
current_time = pd.Timestamp.now().normalize()  # Current date rounded to midnight
two_weeks_ago = current_time - pd.Timedelta(weeks=2)  # Two weeks ago

# Filter tasks from the last two weeks with frequency 1 or 2
recent_tasks = not_a_database[
    (not_a_database['time'] >= two_weeks_ago) &
    (not_a_database['time'] < current_time) &
    (not_a_database['frequency'].isin([1, 2]))
]

# Duplicate recurring tasks and update their timestamps for the next occurrence(s)
new_entries = []
for _, row in recent_tasks.iterrows():
    if row['frequency'] == 1:
        # Task repeats every week
        next_occurrence = row['time'] + pd.Timedelta(weeks=1)
        
    elif row['frequency'] == 2:
        # Task repeats every two weeks
        next_occurrence = row['time'] + pd.Timedelta(weeks=2)
    else:
        continue

    # Create a new row with the updated time for the recurring task
    new_row = row.copy()
    new_row['time'] = next_occurrence
    new_entries.append(new_row)

# Append the new entries to the database
if new_entries:
    new_data = pd.DataFrame(new_entries, columns=header)
    not_a_database = pd.concat([not_a_database, new_data], ignore_index=True)

# Save the updated database back to the CSV file
not_a_database.to_csv('notadatabase.csv', index=False)
print("Database updated with recurring tasks.")
