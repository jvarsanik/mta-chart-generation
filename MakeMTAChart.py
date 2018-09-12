# Code to read output from teamgantt and the combine it into a csv file from which we can make MTA charts

# import libraries
import csv
import os
import os.path
from shutil import copyfile, copy

from datetime import date, datetime, timedelta
from dateutil.parser import parse

# Plotting
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# FUnctions!
def calculateLevel(task_number):
    return len(task_number.split('.'))

def calculateTopParentTask(task_number):
    split_num = task_number.split('.')
    return split_num[0] + '.' + split_num[1]

def convertToDate(date_in):
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

# inpout parameters
#TASKS_TO_PLOT = ['Sensor', 'Data Viewer', 'Summary Views']

DNAME_IN = 'output'


# Check for CURRENT.csv
data_fname = os.path.join(DNAME_IN, 'CURRENT.csv')

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
task_names = []
end_dates = []
task_numbers = []
levels = []
top_parents = []
latest_end_dates = []

end_dates_dict = {}

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

    # Check that we have dates
    is_good = True
    for this_date in these_end_dates:
        if not this_date:
            is_good = False
            break
    
    if not is_good:
        continue

    # Update all the data holders
    task_numbers.append(this_task_number)
    task_names.append(this_task_name)
    end_dates.append(these_end_dates)
    latest_end_dates.append(max(these_end_dates))
    end_dates_dict[this_task_name] = these_end_dates
    levels.append(this_level)
    top_parents.append(calculateTopParentTask(this_task_number))


# close the csv file (bad practivce, shoud do in t with...)
csvfile.close()


# Sort the arrays, to plot them in the right order (longest on top(plotted first))
inds = range(len(latest_end_dates))
sorted_inds = [x for _,x in sorted(zip(latest_end_dates, inds), reverse=True)]

task_numbers = [task_numbers[i] for i in sorted_inds]
task_names = [task_names[i] for i in sorted_inds]
end_dates = [end_dates[i] for i in sorted_inds]
latest_end_dates = [latest_end_dates[i] for i in sorted_inds]
levels = [levels[i] for i in sorted_inds]
top_parents = [top_parents[i] for i in sorted_inds]

#  Now plot the level you want (will plot this level and above (lower level ( 1st is highest level))
fig, ax = plt.subplots()
n = datetime.now()
this_month = datetime(year=n.year, month=n.month, day=1)
max_date = this_month
min_date = this_month

PLOT_LEVEL = 3

# % update max and min 
if max(dates_calculated) > max_date:
    max_date = max(dates_calculated)

if min(dates_calculated) < min_date:
    min_date = min(dates_calculated)

for i in range(len(task_numbers)):
    this_level = levels[i]

    #print(task_numbers[i])
    # Check level
    if this_level > PLOT_LEVEL:
        continue
    

    #print('Filtering ', end_dates[i])
    end_dates_filtered1, calculated_dates_filtered1 = filterDatesToOnlyPlotDatesWithData(end_dates[i], dates_calculated)

    if not end_dates_filtered1:
        continue


    end_dates_filtered, calculated_dates_filtered = filterEndDatesToNotGoPastCalculatedDate(end_dates_filtered1, calculated_dates_filtered1)

   

    # % update max and min 
    if max(end_dates_filtered) > max_date:
        max_date = max(end_dates_filtered)

    if min(end_dates_filtered) < min_date:
        min_date = min(end_dates_filtered)

    print('Plotting ', task_names[i], ': ',   convertListOfDatesToString(end_dates_filtered))

    # add to plot
    ax.plot(calculated_dates_filtered, end_dates_filtered, label=task_names[i])

# Do plot formatting

# Set the limits
max_date = datetime(max_date.year, max_date.month + 1, 1)
ax.set_xlim(min_date, max_date)
ax.set_ylim(min_date, max_date)

# PLot the target line
target_line_dates = [min_date, max_date]
ax.plot(target_line_dates, target_line_dates, color='black')

# adjust the lavels
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.format_ydata = mdates.DateFormatter('%Y-%m-%d')
fig.autofmt_xdate()


#  Show the legend
ax.legend()

# show the plot
plt.show()
