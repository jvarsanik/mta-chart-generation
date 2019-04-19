''' Make Template file from ClickUp Output

NOTE + NEEDED TO STOP _ NERER ARE THOUGHTS!!!
 - this does not work - will geep a global running lkist of the nubmer of tasks, etc, wont' restart for each new list, etc.
 - need to have dict that holds lists...  So, the project list is a dict, with the key as the space names.  The values are lists of projects that we add to.  The index of the project in the list is the list number.
 - for list, the key is "space + ',' + project"
 - so to get number, see if 'list name' is in list, if not, append it to the list.  Return the index of 'list name' in the list...

'''

import os
import csv

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

def getSpaceNumberOLD(space_name):
    # If we have seen this space before, just return its number, if we have not, increment the counter, 
    # add it to the dict, and return that number
    global space_number
    if space_name not in space_list:
        space_count = space_count + 1
        space_list[space_name] = space_count

    return space_list[space_name]

def getSpaceNumber(space_name, space_list):
    # If we have seen this space before, just return its number, if we have not, increment the counter, 
    # add it to the dict, and return that number
    if space_name not in space_list:
        space_list.append(space_name)

    return space_list.index(space_name) + 1

def getProjectNumber(project_name):
    # If we have seen this project before, just return its number, if we have not, increment the counter, 
    # add it to the dict, and return that number
    if project_name not in project_list:
        project_count = project_count + 1
        project_list[project_name] = project_count

    return project_list[project_name]

def getListNumber(list_name):
    # If we have seen this list before, just return its number, if we have not, increment the counter, 
    # add it to the dict, and return that number
    if list_name not in list_list:
        list_count = list_count + 1
        list_list[list_name] = list_count

    return list_list[list_name]

def getTaskNumber(task_id):
    # If we have seen this task before, just return its number, if we have not, increment the counter, 
    # add it to the dict, and return that number
    if task_id not in task_list:
        task_count = task_count + 1
        task_list[task_id] = task_count

    return task_list[task_id]

def getSubtaskNumber(subtask_id):
    # If we have seen this subtask_count before, just return its number, if we have not, increment the counter, 
    # add it to the dict, and return that number
    if subtask_id not in subtask_list:
        subtask_count = subtask_count + 1
        subtask_list[subtask_id] = subtask_count

    return subtask_list[subtask_id]


def getThingNumberOLD(thing_name, thing_list, thing_count):
    # If we have seen this subtask_count before, just return its number, if we have not, increment the counter, 
    # add it to the dict, and return that number
    if thing_name not in thing_list:
        thing_count = thing_count + 1
        thing_list[thing_name] = thing_count

    return thing_list[thing_name]


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
## MAIN FUNCTION
###############################################

DNAME_IN = os.path.join('input', 'ClickUp')

fname_in = '12252683qcht7zn.csv'

full_fname_in = os.path.join(DNAME_IN, fname_in)

# # ClickUp only has 5 possible levels: Space, Project, List, Task, Subtask  (all tasks MUST have the first 4 levels, 5th is optional)
# # Make holders for this information on each task, as a dictionary with the key as the task id
# space_list = {}
# project_list = {}
# list_list = {}
# task_list = {}
# subtask_list = {}

# space_count = 0
# project_count = 0
# list_count = 0
# task_count = 0
# subtask_count = 0

space_header = "Space Name"
project_header = "Project Name"
list_header = "List Name"
task_parent_header = "Parent ID"
task_id_header = "Task ID"

with open(full_fname_in, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        # Get all the values
        space_name = row[space_header]
        project_name = row[project_header]
        list_name = row[list_header]
        parent_id = row[task_parent_header]
        task_id = row[task_id_header]

        # Get Space Number
        # Call getSpaceNumber Function
            # If Space Name exists as a key in dictionary, then return that number, if not, increment our global counter of spaces and return that number
        # space_number = getThingNumber(space_name, space_list, space_count)
        space_number = getSpaceNumber(space_name, space_list)
        # print(f'\t{space_number}')
        # space_number = getThingNumber(space_name, space_list, space_count)
        # print(f'\t{space_number}')

        # Call getProjectNumber
        # project_number = getProjectNumber(space_name + "," + project_name)
        # print(f'\t{project_number}')
        # project_number = getThingNumber(space_name + "," + project_name, project_list, project_count)
        project_number = getThingNumber(project_name, project_list, space_name)
        # print(f'\t{project_number}')

        # Call getListNumber
        # list_number = getListNumber(space_name + "," + project_name + "," + list_name)
        # print(f'\t{list_number}')
        # list_number = getThingNumber(space_name + "," + project_name + "," + list_name, list_list, list_count)
        list_number = getThingNumber(list_name, list_list, space_name + "," + project_name)
        # print(f'\t{list_number}')

        # If parent is not null, call getTaskNumber with Parent ID, if parent is null, call getTaskNumber with Task ID
        if parent_id == 'null':
            # task_number = getTaskNumber(task_id)
            # print(f'\t{task_number}')
            # task_number = getThingNumber(task_id, task_list, task_count)
            task_number = getThingNumber(task_id, task_list, space_name + "," + project_name + "," + list_name)
            # print(f'\t{task_number}')
            subtask_number = -1
        # If parent is not null, call getSubtaskNumber with Task ID
        else:
            # task_number = getTaskNumber(parent_id)
            # subtask_number = getSubtaskNumber(space_name + "," + project_name + "," + list_name + "," + parent_id)
            # print(f'\t{subtask_number}')
            # task_number = getThingNumber(parent_id, task_list, task_count)
            task_number = getThingNumber(parent_id, task_list, space_name + "," + project_name + "," + list_name)
            # subtask_number = getThingNumber(space_name + "," + project_name + "," + list_name + "," + parent_id, subtask_list, subtask_count)
            subtask_number = getThingNumber(task_id, subtask_list, space_name + "," + project_name + "," + list_name + "," + parent_id)
            # print(f'\t{subtask_number}')
        # Now, make the hierarchical task number
        hierarchical_task_number = str(space_number) + '.' + str(project_number) + '.' + str(list_number) + '.' + str(task_number)
        if subtask_number > 0:
            hierarchical_task_number = hierarchical_task_number + '.' + str(subtask_number)

        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        print(f'\t{space_name} - {project_name} - {list_name} - {parent_id} - {task_id} ==> {hierarchical_task_number}')
        line_count += 1
    print(f'Processed {line_count} lines.')


# Now, assign unique hierarchical task ids: (i.e. 3.1.1.2 means it is the second task of the list subtask of the first project in the third space)

# generate a task key with the name of the Space, Project, List, and (if not == null) ParentID.
# Look in dictionary tracking running task numbers.  If the key exists, this task is the existing number in that dict +1 (and update the dict...)
# Get Space, Project, and List numberd from unique list generated above...


