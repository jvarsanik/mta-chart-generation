''' Read tasks from ClickUp Output and generate hierarchical task numbers

'''

import os
import csv
import datetime

from Task import Task, TaskList

###############################################
## HELPERS - GET NUMBERS FOR TASK< SPACE< ETC
###############################################
# ClickUp only has 5 possible levels: Space, Project, List, Task, Subtask  (all tasks MUST have the first 4 levels, 5th is optional)
# Make holders for this information on each task, as a dictionary with the key as the task id
# Can move thes lower, once we switch to generic getThingNumber
space_list = [] #{}
project_list = {}
list_list = {}
task_list = {}
subtask_list = {}

space_count = 0
project_count = 0
list_count = 0
task_count = 0
subtask_count = 0


def getSpaceNumber(space_name, space_list):
    # If we have seen this space before, just return its number, if we have not, increment the counter, 
    # add it to the dict, and return that number
    if space_name not in space_list:
        space_list.append(space_name)

    return space_list.index(space_name) + 1



def getThingNumber(thing_name, thing_list, thing_key):
    # If we have seen this subtask_count before, just return its number, if we have not, increment the counter, 
    # add it to the dict, and return that number
    if thing_key in thing_list:
        this_list = thing_list[thing_key]

        if thing_name not in this_list:
            thing_list[thing_key].append(thing_name)

    else:
        thing_list[thing_key] = [thing_name]

    return thing_list[thing_key].index(thing_name) + 1
    

###############################################
## MAIN FUNCTION - read data form file
###############################################
space_header = "Space Name"
project_header = "Project Name"
list_header = "List Name"
task_parent_header = "Parent ID"
task_id_header = "Task ID"
task_name_header = "Task Name"
enddate_header = "Due Date"

def load_tasks_from_file(full_fname_in):

    ALL_TASKS = []
    ALL_TASK_LIST = TaskList()

    # Get all rows from csv file and store in intermediate variable
    with open(full_fname_in, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        ALL_ROWS = []
        for row in csv_reader:
            this_row = row
            enddate_str = row[enddate_header]
            if len(enddate_str) > 0:
                enddate = datetime.datetime.fromtimestamp(int(enddate_str)/1000)
            else:
                enddate = datetime.datetime.fromtimestamp(0)

            this_row['enddate'] = enddate
            ALL_ROWS.append(this_row)
        
    # Sort them by enddate, so subtask hierarchy is in time order (clickup output is not necessarioy in time order)
    ALL_ROWS.sort(key=lambda x: str(x['enddate']) + x[task_name_header].lower())

    for row in ALL_ROWS:
        
        # Get all the values
        space_name = row[space_header]
        project_name = row[project_header]
        list_name = row[list_header]
        parent_id = row[task_parent_header]
        task_id = row[task_id_header]
        task_name = row[task_name_header]
        enddate_str = row[enddate_header]
        if len(enddate_str) > 0:
            enddate = datetime.datetime.fromtimestamp(int(enddate_str)/1000)
        else:
            enddate = None

        # Get Space Number
        space_number = getSpaceNumber(space_name, space_list)

        # Call getProjectNumber
        project_number = getThingNumber(project_name, project_list, space_name)

        # Call getListNumber
        list_number = getThingNumber(list_name, list_list, space_name + "," + project_name)

        # If parent is not null, call getTaskNumber with Parent ID, if parent is null, call getTaskNumber with Task ID
        if parent_id == 'null':
            task_number = getThingNumber(task_id, task_list, space_name + "," + project_name + "," + list_name)
            subtask_number = -1
            task_level = 4
        # If parent is not null, call getSubtaskNumber with Task ID
        else:
            task_number = getThingNumber(parent_id, task_list, space_name + "," + project_name + "," + list_name)
            subtask_number = getThingNumber(task_id, subtask_list, space_name + "," + project_name + "," + list_name + "," + parent_id)
            task_level = 5

        # Now, make the hierarchical task number
        hierarchical_task_number = str(space_number) + '.' + str(project_number) + '.' + str(list_number) + '.' + str(task_number)
        if subtask_number > 0:
            hierarchical_task_number = hierarchical_task_number + '.' + str(subtask_number)

        # Increment a counter for fun
        line_count += 1

        # Make the task object and append to lsit of tasks
        this_task = (hierarchical_task_number, f'{space_name} - {project_name} - {list_name} - {parent_id} - {task_id} == {task_name}')
        ALL_TASKS.append(this_task)
        ALL_TASK_LIST.add(Task(task_name, hierarchical_task_number, enddate))

        # Make the list of unique hierarchical task numbers
        task_parts = hierarchical_task_number.split('.')
        task_part_names = [space_name, project_name, list_name]
        #for i in range(len(task_parts)-1):

        # Clickup tasks have a a minimum 4 levels.  Create the higher-level bins (levels 1-3)
        # DO it in reverse order so can propagate endate more efficiently
        for i in reversed(range(1,4)):
            this_task_part = ".".join(task_parts[:i])
            this_task_part_name = " - ".join(task_part_names[:i])
            this_single_task_part_name = task_part_names[i-1]

            if not (this_task_part, this_task_part_name) in ALL_TASKS:
                ALL_TASKS.append((this_task_part, this_task_part_name))
                ALL_TASK_LIST.add(Task(this_single_task_part_name, this_task_part))
        print(f'Processed {line_count} lines.')


        

    # Sort the tasks and display
    # print("ALL TASKS:")
    # for (task_number, task_description) in ALL_TASKS:
    #     print(task_number, ' == ', task_description)
    
    # for task in ALL_TASK_LIST:
    #     print('\tTask: ', task.task_number, '\t ', task.name, ' \t - enddate ', task.enddate)

    # Return the task list 
    return ALL_TASK_LIST


###############################################
## MAIN FUNCTION
###############################################

if __name__ == "__main__":

    DNAME_IN = os.path.join('input', 'ClickUp')

    fname_in = '12252683qcht7zn.csv'

    full_fname_in = os.path.join(DNAME_IN, fname_in)

    load_tasks_from_file(full_fname_in)



