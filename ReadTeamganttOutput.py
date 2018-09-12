# Code to read output from teamgantt and the combine it into a csv file from which we can make MTA charts

# import libraries
import csv
import os
import os.path
from datetime import date
from shutil import copyfile, copy

# inpout parameters
#TASKS_TO_PLOT = ['Sensor', 'Data Viewer', 'Summary Views']

DNAME_IN = 'input'
DNAME_OUT = 'output'

task_name_header  = 'Name / Title'
end_date_header = 'End Date'
task_number_header = 'WBS #'

# get info 
todays_date = date.today().strftime('%Y%m%d')
todays_date_pretty = date.today().strftime('%m/%d/%Y')

# get directory listing


# for each file, then read it
fname = 'ExampleTeamGanttOutput.csv'

fname_full = os.path.join(DNAME_IN, fname)

# get the headers to get the column labels
csvfile = open(fname_full)
dreader = csv.DictReader(csvfile)

# Initialize the holders
task_names = []
end_dates = []
task_numbers = []
end_dates_dict = {'Date Calculated' : todays_date_pretty}

# loop through file and populate the holders
for line in dreader:
    # if we are tracking this task, add it to the dict
    #if line[task_name_header] in TASKS_TO_PLOT:
    end_dates_dict[line[task_name_header]] = line[end_date_header]

    # append to arrays, for fun
    task_names.append(line[task_name_header])
    end_dates.append(line[end_date_header])
    task_numbers.append(line[task_number_header])

# close the csv file (bad practivce, shoud do in t with...)
csvfile.close()

#print(end_dates_dict)

# Open template outpout and append to the completion dates...
template_fname = os.path.join(DNAME_OUT, 'CURRENT.csv')
current_fname = template_fname
output_fname = os.path.join(DNAME_OUT, todays_date + '.csv')

if not os.path.isfile(template_fname):
    template_fname = os.path.join(DNAME_OUT, 'EXAMPLE_TEMPLATE.csv')

t = open(template_fname)
o = open(output_fname, 'w')

reader = csv.reader(t)
writer = csv.writer(o)

for line in reader:
    print("line in: ", line)
    if line[1] in end_dates_dict:
        line.append(end_dates_dict[line[1]])


    writer.writerow(line)
    print('line out: ', line)

# close things
t.close()
o.close()

# copy to current
copy(output_fname, current_fname)
