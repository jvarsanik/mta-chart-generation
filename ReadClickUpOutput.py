''' Read ClickUp files from a directory, import each of them and combine them into a .csv file for making an MTA chart.

Function:
    Reads all files in `input` folder matching `file_prefix` and combines the end dates for each task into a .csv file that can then be used to make an MTA chart with `MakeMTAChart.py`

Input:
    Exported data from ClickUp - MUST CHANGE NAME OF FILE TO BE IN FORMAT: ClickUp_YYYY-MM-DD.csv

Output:
    Format: .csv file
    First row:  headers and dates calculated: 
        First cell is blank, 
        Second cell is "Date Calculated" 
        Each following cell is the date that the end date estimates were generated.
    Each following row is a task. 
        First cell is heirarchical task number (i.e. 1.1.2 means it is the second subtask of the first subtask of the first major task)
        Second cell is the task name
        Each following cell is the projeted (or actual) completion date for this task

    Example:
        ,	Date Calculated,	9/25/18,	10/1/18	,   10/9/18
        1,	    Tech Team,	    11/9/18,	11/9/18,    11/9/18
        1.1,	Demo,	        10/23/18,	10/26/18,	10/26/18
        1.1.1,	Sensor,	        10/15/18,	10/15/18,	10/15/18


'''

import os
from shutil import copyfile, copy

from datetime import date
import dateutil.parser as dparser

from Task import Task, TaskList, TaskListArray
import clickup_file_importer 


# User variables
DNAME_IN = os.path.join('input', 'ClickUp')
file_prefix = 'ClickUp'

DNAME_OUT = 'output'

# fname_in = 'ExampleTeamGanttOutput.csv'
fname_out = 'CurrentClickUpOutput.csv'


def main():
    # Initialize
    todays_date = date.today().strftime('%Y%m%d')

    this_task_list_array = TaskListArray()

    # Get file
    #fname_in = '12252683qcht7zn.csv'
    #full_fname_in = os.path.join(DNAME_IN, fname_in)

    # Loop through each file
    for fname_in in os.listdir(DNAME_IN):
        if fname_in.startswith(file_prefix):
            # Print update
            print('Reading ', fname_in)

            # Parse the date from the filename
            calculated_date_datetime = dparser.parse(fname_in.replace('_', ':'), fuzzy=True)
            calculated_date_string_pretty = calculated_date_datetime.strftime('%m/%d/%Y')

            # parse it and add it to the array
            full_fname_in = os.path.join(DNAME_IN, fname_in)
            this_task_list = clickup_file_importer.load_tasks_from_file(full_fname_in)
            this_task_list_array.add(this_task_list, calculated_date_string_pretty)


    # output to csv
    output_fname = os.path.join(DNAME_OUT, todays_date + '-ClickUp.csv')
    this_task_list_array.output_to_csv(output_fname)

    # copy to current
    current_fname = os.path.join(DNAME_OUT, fname_out)  # final output name "current"
    print('Done writing, copying to ', current_fname)
    copy(output_fname, current_fname)

    print('DONE')


if __name__ == "__main__":
    main()