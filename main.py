import csv
import os
import json
import cohere

co = cohere.ClientV2(api_key="YOUR_COHERE_API_KEY")

# Define the days for two weeks
days = [
    'Monday Week1', 'Tuesday Week1', 'Wednesday Week1', 'Thursday Week1', 'Friday Week1',
    'Monday Week2', 'Tuesday Week2', 'Wednesday Week2', 'Thursday Week2', 'Friday Week2'
]

# Define working hours from 9:00 to 17:00 in half-hour increments
time_slots = [hour + minute for hour in range(9, 17) for minute in (0.0, 0.5)]

class Appointment:
    def __init__(self, day, start_time, duration, recurrence, description):
        self.day = day
        self.start_time = start_time
        self.duration = duration
        self.recurrence = recurrence.lower()
        self.description = description

    def __repr__(self):
        return (f"Appointment(day={self.day}, start_time={self.start_time}, "
                f"duration={self.duration}, recurrence={self.recurrence}, "
                f"description='{self.description}'), recurrurance={self.recurrence}")

class Schedule:
    def __init__(self):
        # Initialize the schedule dictionary
        self.schedule = {day: [] for day in days}

        # Read existing appointments from 'notadatabase.csv' if it exists
        if os.path.exists('notadatabase.csv'):
            print("Loading existing schedule from 'notadatabase.csv'...")
            with open('notadatabase.csv', 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    day = row['Day']
                    if day in self.schedule:
                        start_time_str = row['Start Time']
                        duration = float(row['Duration'])
                        description = row['Description']
                        # Convert start_time_str to float
                        start_time = self.time_str_to_float(start_time_str)
                        reoccurrence = row['Reoccurrence']
                        appointment = Appointment(day, start_time, duration, reoccurrence, description)
                        self.schedule[day].append(appointment)
            print("Existing schedule loaded.")
        else:
            print("No existing schedule found. Starting with an empty schedule.")

    def time_str_to_float(self, time_str):
        hour, minute = map(int, time_str.split(':'))
        return hour + (0.5 if minute == 30 else 0.0)

    def float_to_time_str(self, time_float):
        hour = int(time_float)
        minute = '30' if time_float % 1 else '00'
        return f"{hour}:{minute}"

    def is_time_slot_free(self, day, start_time, duration):
        # Check if the time slot is free, considering the half-hour break
        appointments = self.schedule[day]
        end_time = start_time + duration

        # Include half-hour break after the appointment
        end_time_with_break = end_time + 0.5

        for appt in appointments:
            appt_start = appt.start_time
            appt_end = appt.start_time + appt.duration
            # Include half-hour break after existing appointments
            appt_end_with_break = appt_end + 0.5

            # Check for overlapping appointments
            if not (end_time_with_break <= appt_start or start_time >= appt_end_with_break):
                return False
        return True

    def add_appointment(self, appointment):
        # Add appointment based on recurrence
        added = False
        if appointment.recurrence == 'single':
            if self.is_time_slot_free(appointment.day, appointment.start_time, appointment.duration):
                self.schedule[appointment.day].append(appointment)
                added = True
            else:
                return False
        elif appointment.recurrence == 'weekly':
            for week in ['Week1', 'Week2']:
                day = appointment.day.replace('Week1', week).replace('Week2', week)
                if self.is_time_slot_free(day, appointment.start_time, appointment.duration):
                    new_appt = Appointment(day, appointment.start_time, appointment.duration, 'weekly', appointment.description)
                    self.schedule[day].append(new_appt)
                    added = True
                else:
                    print(f"Time slot is not free on {day} for weekly appointment.")
                    return False
        elif appointment.recurrence == 'biweekly':
            # Only add to Week1
            if 'Week1' in appointment.day:
                if self.is_time_slot_free(appointment.day, appointment.start_time, appointment.duration):
                    self.schedule[appointment.day].append(appointment)
                    added = True
                else:
                    return False
            else:
                print("Biweekly appointment can only be scheduled in Week1.")
                return False
        else:
            print("Invalid recurrence type. Choose 'single', 'weekly', or 'biweekly'.")
            return False

        if added:
            print(f"Added {appointment}")
            return True
        else:
            print("Time slot is not free.")
            return False

    def save_to_csv(self, filename):
        # Save the schedule to a CSV file
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Day', 'Start Time', 'Duration', 'Description', 'Reoccurrence']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for day in days:
                for appt in sorted(self.schedule[day], key=lambda x: x.start_time):
                    writer.writerow({
                        'Day': day,
                        'Start Time': self.float_to_time_str(appt.start_time),
                        'Duration': appt.duration,
                        'Description': appt.description,
                        'Reoccurrence': appt.recurrence
                    })
        print(f"Schedule saved to {filename}")

# Functions to be used by the Cohere API
def schedule_appointment_function(day: str, week: str, start_time: str, duration: float, recurrence: str, description: str) -> dict:
    """
    Function to schedule an appointment.
    """
    global global_schedule
    day_formatted = f"{day.capitalize()} {week.capitalize()}"
    if day_formatted not in days:
        return {"success": False, "message": "Invalid day or week."}

    # Convert start_time string to float
    try:
        start_time_float = float(start_time)
        if start_time_float not in time_slots:
            return {"success": False, "message": "Invalid start time."}
    except ValueError:
        return {"success": False, "message": "Start time must be a number."}

    appointment = Appointment(day_formatted, start_time_float, duration, recurrence, description)
    result = global_schedule.add_appointment(appointment)
    if result:
        print("Cohere sceduled the appointement.")
        return {"success": True, "message": "Appointment scheduled successfully."}
    else:
        print("Cohere could not schedule the appointement.")
        return {"success": False, "message": "Time slot is not free."}

# Map function names to actual functions
functions_map = {
    "schedule_appointment": schedule_appointment_function
}

# Define the tool for the Cohere API
tools = [
    {
        "type": "function",
        "function": {
            "name": "schedule_appointment",
            "description": "Schedules an appointment if the time slot is free.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "Day of the appointment (e.g., 'Monday')."
                    },
                    "week": {
                        "type": "string",
                        "description": "Week of the appointment ('Week1' or 'Week2')."
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in float format (e.g., '9.0' for 9:00 AM, '9.5' for 9:30 AM)."
                    },
                    "duration": {
                        "type": "number",
                        "description": "Duration of the appointment in hours (e.g., 1.0)."
                    },
                    "recurrence": {
                        "type": "string",
                        "description": "Recurrence type ('single', 'weekly', 'biweekly')."
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the appointment."
                    }
                },
                "required": ["day", "week", "start_time", "duration", "recurrence", "description"]
            }
        }
    }
]

# Preamble and user message
preamble = """
You are an assistant that helps schedule appointments. When a user asks to schedule an appointment, you should use the 'schedule_appointment' function to schedule it.
"""

# Global Schedule instance
global_schedule = Schedule()

def main():
    # Messages for the conversation
    messages = [
        {"role": "system", "content": preamble}
    ]

    print("Welcome to the Appointment Scheduler.")
    print("Type '/save' at any time to save the schedule.")
    print("Type '/exit' or '/quit' to end the session.\n")

    while True:
        # User input
        user_message = input("You: ")
        if user_message.lower() in ['/exit', '/quit']:
            print("Goodbye!")
            break
        elif user_message.lower() == '/save':
            global_schedule.save_to_csv('notadatabase.csv')
            print("Schedule saved to 'notadatabase.csv'.")
            continue

        messages.append({"role": "user", "content": user_message})

        # Call the Cohere API to decide on tool use
        response = co.chat(
            model="command-r-plus-08-2024",
            messages=messages,
            tools=tools
        )

        print("The model recommends doing the following tool calls:\n")

        print("Tool plan:")

        print(response.message.tool_plan, "\n")

        print("Tool calls:")

        if response.message.tool_calls is not None:

            for tc in response.message.tool_calls:

                print(f"Tool name: {tc.function.name} | Parameters: {tc.function.arguments}")
        
            messages.append(

                {

                    "role": "assistant",

                    "tool_calls": response.message.tool_calls,

                    "tool_plan": response.message.tool_plan,

                }

            )

            for tc in response.message.tool_calls:
                # here is where you would call the tool recommended by the model, using the parameters recommended by the model

                tool_result = functions_map[tc.function.name](**json.loads(tc.function.arguments))
                print("TOOL RESULT:", tool_result)

                # store the output in a list

                tool_content = []

                for data in tool_result.values():
                    print("DATA:", data)

                    tool_content.append({"type": "document", "document": {"data": json.dumps(data)}})


                print("TOOL CONTENT:", tool_content)
                messages.append(

                    {"role": "tool", "tool_call_id": tc.id, "content": tool_content}

                )
                print("Tool results that will be fed back to the model in step 4:")

                for result in tool_content:

                    print(result)

       
        response = co.chat(
        model="command-r-plus-08-2024",
        messages=messages,
        tools=tools
        )

        print("Cohere:")
        print(response.message.content[0].text)

if __name__ == "__main__":
    main()
