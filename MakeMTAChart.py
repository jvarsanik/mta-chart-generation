# Code to read output from teamgantt and the combine it into a csv file from which we can make MTA charts

# import libraries
import csv
import os
import os.path
from shutil import copyfile, copy

# Dates
from datetime import date, datetime, timedelta
from dateutil.parser import parse

# Plotting
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Polygon

# numpy 
import numpy as np

# User variables
PLOT_LEVEL = 4
DNAME_IN = 'output'
FNAME_IN = 'TechTeamCurrent.csv'

TASKS_TO_INCLUDE = ['1.1.2']
TASKS_TO_EXCLUDE = []

# FUnctions!
def calculateLevel(task_number):
    return len(task_number.split('.'))

def calculateTopParentTask(task_number):
    split_num = task_number.split('.')
    return split_num[0] + '.' + split_num[1]

def isSubtask(task_number, super_task_number):
    
    this_val =  task_number.startswith(super_task_number)
    if this_val == True:
        print('Task', task_number, ' IS subtask of ', super_task_number)
    else:
        print('Task', task_number, ' IS NOT subtask of ', super_task_number)

    return this_val

def checkIfShouldInclude(task_number):
    # First, check if this task is explicitly included
    if TASKS_TO_INCLUDE:
        for task in TASKS_TO_INCLUDE:
            if isSubtask(task_number, task):
                return True
        
        # if get here, have a list of tasks to include, and task_number is not in them, so exclude
        return False
    
    # Next, check if the task is exploicitly excluded
    if TASKS_TO_EXCLUDE:
        for task in TASKS_TO_EXCLUDE:
            if isSubtask(task_number, task):
                return False
        
        # if get here, have a list of tasks to exclude, and task_number is not in them, so include
        return True

def convertToDate(date_in):
    date_in = date_in.strip()
    #return datetime.strptime(date_in, '%m/%d/%Y')
    date_out = ''
    if not date_in:
        return ''
    else:
        return parse(date_in)

def convertListToDates(dates_in):
    return [convertToDate(x) for x in dates_in]

def convertDateToString(date_in):
    return date_in.strftime('%Y-%m-%d')

def convertListOfDatesToString(dates_in):
    return [convertDateToString(x) for x in dates_in]

def filterEndDatesToNotGoPastCalculatedDate(end_dates, calculated_dates):
    end_dates_filtered = []
    calculated_dates_filtered = []
    is_completed = False
    for i in range(len(end_dates)):
        if end_dates[i] > calculated_dates[i]:
            end_dates_filtered.append(end_dates[i])
            calculated_dates_filtered.append(calculated_dates[i])
        else:
            end_dates_filtered.append(end_dates[i])
            calculated_dates_filtered.append(end_dates[i])
            break

    return end_dates_filtered, calculated_dates_filtered

def filterDatesToOnlyPlotDatesWithData(end_dates, calculated_dates):
    end_dates_filtered = []
    calculated_dates_filtered = []

    for i in range(len(end_dates)):
        if end_dates[i]:
            end_dates_filtered.append(end_dates[i])
            calculated_dates_filtered.append(calculated_dates[i])

    return end_dates_filtered, calculated_dates_filtered

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


## Script is here
# Check for CURRENT.csv
data_fname = os.path.join(DNAME_IN, FNAME_IN)

if not os.path.isfile(data_fname):
    print('No CURRENT.csv file at location: ', data_fname)

# get the headers to get the column labels
csvfile = open(data_fname)
reader = csv.reader(csvfile)

#  get the header row:
row1 = next(reader)
dates_calculated_str = row1[2:]
dates_calculated = convertListToDates(dates_calculated_str)

# ensure these dates are in order!

# Initialize the holders
task_objs = []
latest_end_dates = []

# loop through file and populate the holders
for line in reader:

    this_task_number = line.pop(0)
    this_task_name = line.pop(0)

    # if this_task_name == 'WebUI - API for new user':
    #     print('Pause here')

    if not this_task_number:
        continue

    this_level = num(calculateLevel(this_task_number))

    # Skip level 1 (this is just the project header...)
    if this_level < 2:
        continue

    these_end_dates = convertListToDates(line)

    # Check that we have dates
    # is_good = True
    # for this_date in these_end_dates:
    #     if not this_date:
    #         is_good = False
    #         break
    
    # if not is_good:
    #     continue


    # Filter the dates to only plot dates with data
    end_dates_filtered1, calculated_dates_filtered1 = filterDatesToOnlyPlotDatesWithData(these_end_dates, dates_calculated)

    if not end_dates_filtered1:
        continue

    # filter dates so the lines stop when they hit their completion date
    end_dates_filtered, calculated_dates_filtered = filterEndDatesToNotGoPastCalculatedDate(end_dates_filtered1, calculated_dates_filtered1)

    #update the data holder
    this_obj = {}
    this_obj['task_number'] = this_task_number
    this_obj['task_name'] = this_task_name
    this_obj['end_dates'] = end_dates_filtered
    this_obj['latest_end_date'] = max(end_dates_filtered)
    this_obj['calculated_dates'] = calculated_dates_filtered
    this_obj['level'] = this_level
    this_obj['top_parent'] = calculateTopParentTask(this_task_number)

    # put this in the list
    task_objs.append(this_obj)

    # keep list of latest end dates, for sorting later
    latest_end_dates.append(max(end_dates_filtered))


# close the csv file (bad practivce, shoud do in t with...)
csvfile.close()


# Sort the array, to plot them in the right order (longest on top(plotted first))
inds = range(len(latest_end_dates))
sorted_inds = [x for _,x in sorted(zip(latest_end_dates, inds), reverse=True)]

task_objs = [task_objs[i] for i in sorted_inds]

#  Now plot the level you want (will plot this level and above (lower level ( 1st is highest level))
fig, ax = plt.subplots()
n = datetime.now()
this_month = datetime(year=n.year, month=n.month, day=1)
max_date = this_month
min_date = this_month

# % update max and min 
if max(dates_calculated) > max_date:
    max_date = max(dates_calculated)

if min(dates_calculated) < min_date:
    min_date = min(dates_calculated)

# Go through each task and add to plot
for task in task_objs:
    this_level = task['level']
    this_number = task['task_number']
    this_name = task['task_name']
    these_end_dates = task['end_dates']
    thse_calculated_dates = task['calculated_dates']

    #print(task_numbers[i])
    # Check level
    if this_level > PLOT_LEVEL:
        continue

    # Check if shoudl include
    if not checkIfShouldInclude(this_number):
        continue

    # % update max and min 
    if max(these_end_dates) > max_date:
        max_date = max(these_end_dates)

    if min(these_end_dates) < min_date:
        min_date = min(these_end_dates)

    print('Plotting ', this_name, ': ',   convertListOfDatesToString(these_end_dates))

    # add to plot
    ax.plot(thse_calculated_dates, these_end_dates, label=this_name)

# Do plot formatting

# Set the limits
max_date = datetime(max_date.year, max_date.month + 1, 1)
ax.set_xlim(min_date, max_date)
ax.set_ylim(min_date, max_date)

# set the aspect ratio 
ax.set_aspect('equal')

# adjust the grid
# every monday
# mondays = WeekdayLocator(MONDAY)
# months = MonthLocator(range(1, 13), bymonthday=1, interval=3)
# monthsFmt = DateFormatter("%b '%y")

ax.autoscale_view()
#ax.xaxis.grid(False, 'major')
#ax.xaxis.grid(True, 'minor')
ax.grid(True)

# set the axes to be below other elements (so the patch hides the grid)
ax.set_axisbelow(True)

# Plot the triangle to cover the grid in the lower half
# triangle_points = np.array([[min_date, min_date], [max_date, min_date], [max_date, max_date]])
start = mdates.date2num(min_date)
end = mdates.date2num(max_date)
triangle_points = np.array([[start, start], [end, start], [end, end]])
triangle = Polygon(triangle_points, closed=True, color='white')
ax.add_patch(triangle)

# PLot the target line
target_line_dates = [min_date, max_date]
ax.plot(target_line_dates, target_line_dates, color='black')


# adjust the labels
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.format_ydata = mdates.DateFormatter('%Y-%m-%d')
fig.autofmt_xdate()

#  Show the legend
ax.legend()

# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

# show the plot
plt.show()
