import gspread
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range
from google.auth import exceptions
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd
import time

# Define the scope (permissions you need)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Provide the path to your service account JSON file
creds = Credentials.from_service_account_file(
    'secrets.json', scopes=scope)

raw_date = datetime.now()
dt = raw_date.strftime("%m/%d/%y %H:%M:%S")

# Authenticate and create the client
client = gspread.authorize(creds)

file_sheet = "Todolist <3"

scheduled_task_sheet = client.open(file_sheet).worksheet("Task List")


all_scheduled_tasks = scheduled_task_sheet.get_all_values()

sched_task_df = pd.DataFrame(
    all_scheduled_tasks[1:],
    columns=all_scheduled_tasks[0]
)

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
    print('Now uploading tasks for ', Sheet_name, '\n')
    sheet = client.open(file_sheet).worksheet(Sheet_name)
    starting_row = len(sheet.get_all_values()) + 1
    all_current_tasks = sheet.get_all_values()
    current_tasks = list()
    for t in all_current_tasks:
        current_tasks.append(t[0])

    user_tasks_df = sched_task_df[sched_task_df['Sheet Name'] == Sheet_name]
    user_task_list = list(user_tasks_df.itertuples(index=False, name=None))
    final_user_task_list =  [(t[0] + " (" + t[2] +")", t[1], dt) for t in user_task_list]
    
    completed_df_for_sheet = completed_df[completed_df['Sheet From'] == Sheet_name].copy()

    completed_df_for_sheet["Date Finished"] = pd.to_datetime(completed_df_for_sheet["Date Finished"], errors="coerce")
    completed_df_for_sheet = completed_df_for_sheet.dropna(subset=["Date Finished"])

    frequencies = ('Daily', 'Biweekly', 'Weekly', 'Monthly', 'Quarterly')

    for freq in frequencies:
        if freq == 'Daily':
            frequency_task_list = [task for task in final_user_task_list if f"({freq})" in task[0] and task[0] not in current_tasks]
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
                time.sleep(1)
            len_for_freq = len(frequency_task_list)
            starting_row += len_for_freq
            print(freq, 'tasks uploaded for', Sheet_name, "-", len_for_freq, '.')
        
        else:
            if freq == 'Weekly':
                timedelta_days = 6
            elif freq == 'Biweekly':
                timedelta_days = 13
            elif freq == 'Monthly':
                timedelta_days = 28
            elif freq == 'Quarterly':
                timedelta_days = 90
        
            time_cutoff_date = datetime.now() - timedelta(days=timedelta_days)

            period_df = completed_df_for_sheet[completed_df_for_sheet["Date Finished"] > time_cutoff_date]
            user_period_task_list = list(period_df.itertuples(index=False, name=None))
            final_user_period_task_list = [(t[0] + " (" + freq + ")", t[1], dt) for t in user_period_task_list]
            completed_names_this_period = [t[0] for t in final_user_period_task_list]
            frequency_task_list = [task for task in final_user_task_list if f"({freq})" in task[0] and task[0] not in current_tasks and task[0] not in completed_names_this_period]
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
                            time.sleep(1)

            len_for_freq = len(frequency_task_list)
            starting_row += len_for_freq
            print(freq, 'tasks uploaded for', Sheet_name, "-", len_for_freq)
    print('\n')
        
add_for_sheet('Us')

add_for_sheet('Lydia')

add_for_sheet('Chad')