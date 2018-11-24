# Code to read output from teamgantt and the combine it into a csv file from which we can make MTA charts

# import libraries
import csv
import os
import os.path
from shutil import copyfile, copy

# Dates
from datetime import date, datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

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

PLOT_TITLE = 'Tech Team Milestones'
TASKS_TO_INCLUDE = ['1.1.1']
TASKS_TO_EXCLUDE = []

# FUnctions!
def calculateLevel(task_number):
    return len(task_number.split('.'))

def calculateTopParentTask(task_number):
    split_num = task_number.split('.')
    return split_num[0] + '.' + split_num[1]

def isSubtask(task_number, super_task_number):
    this_val =  task_number.startswith(super_task_number)
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

    # If we get here, we do not have a list of tasks to include or exclude, so include everything
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

# Initialize the holders
task_objs = []
latest_end_dates = []

# loop through file and populate the holders
for line in reader:

    this_task_number = line.pop(0)
    this_task_name = line.pop(0)

    if not this_task_number:
        continue

    this_level = num(calculateLevel(this_task_number))

    # Skip level 1 (this is just the project header...)
    if this_level < 2:
        continue

    these_end_dates = convertListToDates(line)

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
    this_obj['latest_end_date'] = end_dates_filtered[-1]
    this_obj['calculated_dates'] = calculated_dates_filtered
    this_obj['level'] = this_level
    this_obj['top_parent'] = calculateTopParentTask(this_task_number)

    # put this in the list
    task_objs.append(this_obj)

    # keep list of latest end dates, for sorting later
    latest_end_dates.append(this_obj['latest_end_date'])


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

if min(dates_calculated) < min_date:
    min_date = min(dates_calculated)

max_date = max(latest_end_dates)

# find range to get amount to shift overlapping plots (for aesthetics)
this_plot_range = max_date-min_date
this_plot_epsilon = this_plot_range / 100

# reset max date
max_date = min_date

# store list of datapoints to detect collisions (so we can offset overlapping plots)
data_points = {}

# Go through each task and add to plot
for task in task_objs:
    this_level = task['level']
    this_number = task['task_number']
    this_name = task['task_name']
    these_end_dates = task['end_dates']
    these_calculated_dates = task['calculated_dates']

    # Check level
    if this_level > PLOT_LEVEL:
        continue

    # Check if shoudl include
    if not checkIfShouldInclude(this_number):
        continue

    # % update max and min 
    if max(these_end_dates) > max_date:
        max_date = max(these_end_dates)

    if max(these_calculated_dates) > max_date:
        max_date = max(these_calculated_dates)

    if min(these_end_dates) < min_date:
        min_date = min(these_end_dates)

    # Check for collisions (overlapping data points) - remove a little time until there is no collision
    # Remove time so the ordering of the legend entries is correct (we plot from top down...)
    for ind, this_calculated_date in enumerate(these_calculated_dates):
        while data_points and (this_calculated_date in data_points) and (these_end_dates[ind] in data_points[this_calculated_date]):
            print('Collision for ', this_name, ' on ', this_calculated_date, 'at ' , these_end_dates[ind], ' - adding some time')
            these_end_dates[ind] = these_end_dates[ind] - this_plot_epsilon

        #  Add to all data points store to look for more collisions
        if this_calculated_date in data_points:
            data_points[this_calculated_date].append(these_end_dates[ind])
        else:
            data_points[this_calculated_date] = [these_end_dates[ind]]

    print('Plotting ', this_name, ': ',   convertListOfDatesToString(these_end_dates))

    # add to plot (plotting single points differently)
    if len(these_calculated_dates) < 2:
        ax.plot(these_calculated_dates, these_end_dates, 'o', label=this_name)
    else:
        ax.plot(these_calculated_dates, these_end_dates, label=this_name)

# Do plot formatting

# Set the limits (set to line up with months (if range is large enough)
if min_date + relativedelta(months=4) < max_date:
    max_date = datetime(max_date.year, max_date.month, 1) + relativedelta(months=1)
    min_date = datetime(min_date.year, min_date.month, 1)

else:
    max_date = max_date + timedelta(days=1)
    min_date = min_date - timedelta(days=1)

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
# Make triangle - set zorder to 5 to put above all lines (default zorder 2, patch default is 1)
triangle = Polygon(triangle_points, closed=True, color='white', zorder=5) 
ax.add_patch(triangle)

# PLot the target line
target_line_dates = [min_date, max_date]
ax.plot(target_line_dates, target_line_dates, color='black', zorder=10)

# # put x ticks at top
# ax.xaxis.tick_top()
# ax.xaxis.set_label_position('top') 

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

# put a title and axis labels
plt.title(PLOT_TITLE)
plt.xlabel('Date report generated')
plt.ylabel('Projected completion date')

# show the plot
plt.show()
