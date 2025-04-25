import gspread
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range
from google.auth import exceptions
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

dt = datetime.now().strftime("%m/%d/%y %H:%M:%S")

daily_tasks = [
    ["Make the bed (Daily)", 3, dt]
]
    

# Define the scope (permissions you need)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Provide the path to your service account JSON file
creds = Credentials.from_service_account_file(
    'secrets.json', scopes=scope)

# Authenticate and create the client
client = gspread.authorize(creds)

# Open the Google Sheet by title
sheet = client.open("Todolist").worksheet("Shared") # Or use sheet index/URL

all_current_tasks = sheet.get_all_values()
current_tasks = list()
for t in all_current_tasks:
    current_tasks.append(t[0])

starting_row = len(sheet.get_all_values()) + 1


rule = DataValidationRule(
    condition=BooleanCondition('boolean'),
    showCustomUi=True
)

daily_tasks = [task for task in daily_tasks if task[0] not in current_tasks]

for i, task in enumerate(daily_tasks):
    # Add an empty string for the checkbox column
    task.append("")
    sheet.append_row(task)
    #print(task)
    # Figure out which row this is
    current_row = starting_row + i

    # Add checkbox to column D (4)
    set_data_validation_for_cell_range(sheet, f'D{current_row}', rule)

#print (type(rule))
if len(daily_tasks) > 0:
    print('Upload of daily tasks successful.')
else:
    print('No daily tasks to upload')

completed_sheet = client.open("Todolist").worksheet("Completed Tasks")
sheet_data = completed_sheet.get_all_values()

headers = sheet_data[0]
rows = sheet_data[1:]

completed_df = pd.DataFrame(rows, columns=headers)

completed_df["Date Finished"] = pd.to_datetime(completed_df["Date Finished"], errors="coerce")
completed_df = completed_df.dropna(subset=["Date Finished"])


weekly_tasks = [
    ["Move trash can to curb (Weekly)", 2, dt]

]

week_cutoff_date = datetime.now() - timedelta(days=7)

last_week_df = completed_df[completed_df["Date Finished"] > week_cutoff_date]
last_week_list = last_week_df["Task"].tolist()
#print(last_week_list)

weekly_tasks = [task for task in weekly_tasks if task[0] not in current_tasks]

weekly_tasks = [task for task in weekly_tasks if task[0] not in last_week_list]

starting_row = len(sheet.get_all_values()) + 1

for i, task in enumerate(weekly_tasks):
    # Add an empty string for the checkbox column
    task.append("")
    sheet.append_row(task)
    #print(task)
    # Figure out which row this is
    current_row = starting_row + i

    # Add checkbox to column D (4)
    set_data_validation_for_cell_range(sheet, f'D{current_row}', rule)

if len(weekly_tasks) > 0:
    print('Uploaded weekly tasks.')
else:
    print('No weekly tasks to upload.')

biweekly_tasks = [
    ["Wash bed sheets (Biweekly)", 2, dt]
]

biweek_cutoff_date = datetime.now() - timedelta(days=14)

biweek_df = completed_df[completed_df["Date Finished"] >= biweek_cutoff_date]

biweek_list = biweek_df["Task"].tolist()

biweekly_tasks = [task for task in biweekly_tasks if task[0] not in current_tasks]

biweekly_tasks = [task for task in biweekly_tasks if task[0] not in biweek_list]

starting_row = len(sheet.get_all_values()) + 1

for i, task in enumerate(biweekly_tasks):
    # Add an empty string for the checkbox column
    task.append("")
    sheet.append_row(task)
    #print(task)
    # Figure out which row this is
    current_row = starting_row + i

    # Add checkbox to column D (4)
    set_data_validation_for_cell_range(sheet, f'D{current_row}', rule)

if len(biweekly_tasks) > 0:
    print('Uploaded biweekly tasks.')
else:
    print("No biweekly tasks to upload.")

monthly_tasks = [
    ["Wash car exterior, vacuum interior (Monthly)", 1, dt]
]

month_cutoff_date = datetime.now() - timedelta(days = 30)

month_df = completed_df[completed_df["Date Finished"] >= month_cutoff_date]
month_list = month_df["Task"].tolist()

monthly_tasks = [task for task in monthly_tasks if task[0] not in current_tasks]

monthly_tasks = [task for task in monthly_tasks if task[0] not in month_list]

starting_row = len(sheet.get_all_values()) + 1

for i, task in enumerate(monthly_tasks):
    # Add an empty string for the checkbox column
    task.append("")
    sheet.append_row(task)
    #print(task)
    # Figure out which row this is
    current_row = starting_row + i

    # Add checkbox to column D (4)
    set_data_validation_for_cell_range(sheet, f'D{current_row}', rule)

if len(monthly_tasks) > 0:
    print('Uploaded monthly tasks')
else:
    print("No monthly taks to upload")

quarterly_tasks = [
    ["Deep clean fridge (Quarterly)", 1, dt]
]

quarter_cutoff_date = datetime.now() - timedelta(days = 90)

quarter_df = completed_df[completed_df["Date Finished"] >= quarter_cutoff_date]
quarter_list = quarter_df["Task"].tolist()

quarterly_tasks = [task for task in quarterly_tasks if task[0] not in current_tasks]

quarterly_tasks = [task for task in quarterly_tasks if task[0] not in quarter_list]

starting_row = len(sheet.get_all_values()) + 1

for i, task in enumerate(quarterly_tasks):
    # Add an empty string for the checkbox column
    task.append("")
    sheet.append_row(task)
    #print(task)
    # Figure out which row this is
    current_row = starting_row + i

    # Add checkbox to column D (4)
    set_data_validation_for_cell_range(sheet, f'D{current_row}', rule)

if len(quarterly_tasks) > 0:
    print('Uploaded quarterly tasks.')
else:
    print("No quarterly tasks to upload today.")
