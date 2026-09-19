import gspread
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range
from google.auth import exceptions
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd


# Define the scope (permissions you need)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Provide the path to your service account JSON file
creds = Credentials.from_service_account_file(
    'secrets.json', scopes=scope)

raw_date = datetime.now()
dt = raw_date.strftime("%m/%d/%y %H:%M:%S")

# Authenticate and create the client
client = gspread.authorize(creds)



# Open the Google Sheet by title
#change to the actual file name for prod
file_sheet = "Copy of Todolist <3"


#testing sheet
# sheet = client.open(file_sheet).worksheet("Us") # Or use sheet index/URL


# all_current_tasks = sheet.get_all_values()
# current_tasks = list()
# for t in all_current_tasks:
#     current_tasks.append(t[0])



scheduled_task_sheet = client.open(file_sheet).worksheet("Task List")


all_scheduled_tasks = scheduled_task_sheet.get_all_values()

sched_task_df = pd.DataFrame(
    all_scheduled_tasks[1:],
    columns=all_scheduled_tasks[0]
)

#print(sched_task_df)

# def add_tasks_to_specific_todo_list (Sheet_name, Frequency):
#     user_tasksdf = sched_task_df[(sched_task_df['Sheet Name'] == Sheet_name) &
#                     (sched_task_df['Frequency'] == Frequency)]
#     #if Frequency is "Daily":
#     user_task_list = list(user_tasksdf.itertuples(index=False, name=None))
#     new_list =  [(t[0] + ' )' + t[2] +")", t[1], dt) for t in user_task_list]

#     print(new_list)

# add_tasks_to_specific_todo_list('Lydia', 'Daily') 
rule = DataValidationRule(
    condition=BooleanCondition('boolean'),
    showCustomUi=True
)
frequencies = ('Daily', 'Weekly', 'Monthly', 'Quarterly')

completed_sheet = client.open(file_sheet).worksheet("Completed Tasks")
sheet_data = completed_sheet.get_all_values()

headers = sheet_data[0]
rows = sheet_data[1:]

completed_df = pd.DataFrame(rows, columns=headers)

completed_df["Date Finished"] = pd.to_datetime(completed_df["Date Finished"], errors="coerce")
completed_df = completed_df.dropna(subset=["Date Finished"])


def add_for_sheet (Sheet_name):
    sheet = client.open(file_sheet).worksheet(Sheet_name)
    starting_row = len(sheet.get_all_values()) + 1
    all_current_tasks = sheet.get_all_values()
    current_tasks = list()
    for t in all_current_tasks:
        current_tasks.append(t[0])

    user_tasks_df = sched_task_df[sched_task_df['Sheet Name'] == Sheet_name]
    user_task_list = list(user_tasks_df.itertuples(index=False, name=None))
    final_user_task_list =  [(t[0] + " (" + t[2] +")", t[1], dt) for t in user_task_list]
    print(final_user_task_list)
    completed_df_for_sheet = completed_df[completed_df['Sheet From'] == Sheet_name]

    frequencies = ('Daily', 'Weekly', 'Monthly', 'Quarterly')

    for freq in frequencies:
        if freq == 'Daily':
            frequency_task_list = [task for task in final_user_task_list if task[0] not in current_tasks]
            for i, task in enumerate(frequency_task_list):
                # Add an empty string for the checkbox column
                task = list(task)
                task.append("")
                sheet.append_row(task, value_input_option='USER_ENTERED')
                #print(task)
                # Figure out which row this is
                current_row = starting_row + i

                # Add checkbox to column D (4)
                set_data_validation_for_cell_range(sheet, f'D{current_row}', rule)
        
        else:
            print(freq)
        #completed_df_for_sheet_by_freq = completed_df_for_sheet[completed_df_for_sheet['Frequency'] == freq]
        #print (completed_df_for_sheet_by_freq)

add_for_sheet('Lydia')
exit()

rule = DataValidationRule(
    condition=BooleanCondition('boolean'),
    showCustomUi=True
)

daily_tasks = [
    ["Make the bed (Daily)", 3, dt]
]

daily_tasks = [task for task in daily_tasks if task[0] not in current_tasks]
daily_length = len(daily_tasks)

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
if daily_length  > 0:
    print('Daily tasks uploaded:', daily_length)
else:
    print('No daily tasks to upload')

completed_sheet = client.open(file_sheet).worksheet("Completed Tasks")
sheet_data = completed_sheet.get_all_values()

headers = sheet_data[0]
rows = sheet_data[1:]

completed_df = pd.DataFrame(rows, columns=headers)

completed_df["Date Finished"] = pd.to_datetime(completed_df["Date Finished"], errors="coerce")
completed_df = completed_df.dropna(subset=["Date Finished"])


weekly_tasks = [
    
    ["Mop floor (Weekly)", 2, dt]

]

Monday_tasks = [
    ["Move trash can to curb (Weekly)", 2, dt]
]

week_cutoff_date = datetime.now() - timedelta(days=6)

last_week_df = completed_df[completed_df["Date Finished"] > week_cutoff_date]
last_week_list = last_week_df["Task"].tolist()
#print(last_week_list)

weekly_tasks = [task for task in weekly_tasks if task[0] not in last_week_list]

if raw_date.weekday() == 0:
    for task in Monday_tasks:
        weekly_tasks.append(task)

weekly_tasks = [task for task in weekly_tasks if task[0] not in current_tasks]

weekly_length = len(weekly_tasks)

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

if weekly_length > 0:
    print('Weekly tasks uploaded:', weekly_length)
else:
    print('No weekly tasks to upload.')

biweekly_tasks = [
    ["Wash bed sheets (Biweekly)", 2, dt]
]

biweek_cutoff_date = datetime.now() - timedelta(days=13)

biweek_df = completed_df[completed_df["Date Finished"] >= biweek_cutoff_date]

biweek_list = biweek_df["Task"].tolist()

biweekly_tasks = [task for task in biweekly_tasks if task[0] not in current_tasks]

biweekly_tasks = [task for task in biweekly_tasks if task[0] not in biweek_list]

biweekly_length = len(biweekly_tasks)

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

if biweekly_length > 0:
    print('Biweekly tasks uploaded:', biweekly_length)
else:
    print("No biweekly tasks to upload.")

monthly_tasks = [
    ["Organize pantry (Monthly)", 1, dt]
]

month_cutoff_date = datetime.now() - timedelta(days = 28)

month_df = completed_df[completed_df["Date Finished"] >= month_cutoff_date]
month_list = month_df["Task"].tolist()

monthly_tasks = [task for task in monthly_tasks if task[0] not in current_tasks]

monthly_tasks = [task for task in monthly_tasks if task[0] not in month_list]

monthly_length = len(monthly_tasks)

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

if monthly_length > 0:
    print('Monthly taks uploaded:', monthly_length)
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

quarterly_length = len(quarterly_tasks)

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

if quarterly_length > 0:
    print('Quarterly tasks uploaded:', quarterly_length)
else:
    print("No quarterly tasks to upload today.")


print("\n")
print("It is time to upload tasks for Lydia\n")
#Lyd's tasks

Lyd_sheet = client.open("Todolist <3").worksheet("Lydia") # Or use sheet index/URL

all_Lyd_current_tasks = Lyd_sheet.get_all_values()
Lyd_current_tasks = list()
for t in all_Lyd_current_tasks:
    Lyd_current_tasks.append(t[0])

Lyd_starting_row = len(Lyd_sheet.get_all_values()) + 1

Lyd_daily_tasks = [
    ["Brush teeth morning (Daily)", 3, dt]
]


Lyd_daily_tasks = [task for task in Lyd_daily_tasks if task[0] not in Lyd_current_tasks]
Lyd_daily_length = len(Lyd_daily_tasks)

for i, task in enumerate(Lyd_daily_tasks):
    # Add an empty string for the checkbox column
    task.append("")
    Lyd_sheet.append_row(task)
    #print(task)
    # Figure out which row this is
    current_row = Lyd_starting_row + i

    # Add checkbox to column D (4)
    set_data_validation_for_cell_range(Lyd_sheet, f'D{current_row}', rule)

if Lyd_daily_length > 0:
    print('Total daily tasks for Lydia uploaded:', Lyd_daily_length)
else:
    print("No daily tasks for Lydia to upload today.")


Lyd_weekly_tasks = [
    ["Play piano (Weekly)", 1, dt]
]

Lyd_weekly_tasks = [task for task in Lyd_weekly_tasks if task[0] not in Lyd_current_tasks]

Lyd_weekly_tasks = [task for task in Lyd_weekly_tasks if task[0] not in last_week_list]
Lyd_weekly_length = len(Lyd_weekly_tasks)

Lyd_starting_row = len(Lyd_sheet.get_all_values()) + 1

for i, task in enumerate(Lyd_weekly_tasks):
    # Add an empty string for the checkbox column
    task.append("")
    Lyd_sheet.append_row(task)
    #print(task)
    # Figure out which row this is
    current_row = Lyd_starting_row + i

    # Add checkbox to column D (4)
    set_data_validation_for_cell_range(Lyd_sheet, f'D{current_row}', rule)

if Lyd_weekly_length > 0:
    print('Total weekly tasks for Lydia uploaded:', Lyd_weekly_length)
else:
    print("No weekly tasks for Lydia to upload today.")

print("\n")
print("It is time to upload tasks for Chad\n")

Chad_sheet = client.open("Todolist <3").worksheet("Chad") # Or use sheet index/URL

all_Chad_current_tasks = Chad_sheet.get_all_values()
Chad_current_tasks = list()
for t in all_Chad_current_tasks:
    Chad_current_tasks.append(t[0])

Chad_starting_row = len(Chad_sheet.get_all_values()) + 1

Chad_daily_tasks = [
    ["Brush teeth in morning (Daily)", 3, dt]
]

Chad_daily_work_tasks = [
    ["Active in Omni (Work)", 1, dt]
]


if raw_date.weekday() < 5:
    for task in Chad_daily_work_tasks:
        Chad_daily_tasks.append(task)


Chad_daily_tasks = [task for task in Chad_daily_tasks if task[0] not in Chad_current_tasks]
Chad_daily_length = len(Chad_daily_tasks)

for i, task in enumerate(Chad_daily_tasks):
    # Add an empty string for the checkbox column
    task.append("")
    Chad_sheet.append_row(task)
    #print(task)
    # Figure out which row this is
    current_row = Chad_starting_row + i

    # Add checkbox to column D (4)
    set_data_validation_for_cell_range(Chad_sheet, f'D{current_row}', rule)

if Chad_daily_length > 0:
    print('Total daily tasks for Chad uploaded:', Chad_daily_length)
else:
    print("No daily tasks for Chad to upload today.")