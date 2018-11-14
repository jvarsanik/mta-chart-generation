# Code to read output from teamgantt and the combine it into a csv file from which we can make MTA charts

# import libraries
import csv
import os
import os.path
from datetime import date
from shutil import copyfile, copy

import dateutil.parser as dparser

# inpout parameters
#TASKS_TO_PLOT = ['Sensor', 'Data Viewer', 'Summary Views']

DNAME_IN = 'input'
DNAME_OUT = 'output'

# fname_in = 'ExampleTeamGanttOutput.csv'
fname_out = 'TechTeamCurrent.csv'
base_template = 'TechTeamTemplate.csv' # List of tasks that will be included in output  can just copy first column of input file

file_prefix = 'Tech Team'

task_name_header  = 'Name / Title'
end_date_header = 'End Date'
task_number_header = 'WBS #'

# get today's date
todays_date = date.today().strftime('%Y%m%d')

# Make the blank holder to hold all dates
all_data = {}

# Loop through each file
for fname_in in os.listdir(DNAME_IN):
    if fname_in.startswith(file_prefix):
        # Print update
        print('Reading ', fname_in)

        # get info 
        todays_date = date.today().strftime('%Y%m%d')
        # todays_date_pretty = date.today().strftime('%m/%d/%Y')

        # get info from the filename
        calculated_date_datetime = dparser.parse(fname_in.replace('_', ':'), fuzzy=True)
        calculated_date_string = calculated_date_datetime.strftime('%Y%m%d')
        calculated_date_string_pretty = calculated_date_datetime.strftime('%m/%d/%Y')

        # Read file
        fname_full = os.path.join(DNAME_IN, fname_in)

        # get the headers to get the column labels
        csvfile = open(fname_full)
        dreader = csv.DictReader(csvfile)

        # Initialize the holders
        task_names = []
        end_dates = []
        task_numbers = []
        end_dates_dict = {'Date Calculated' : calculated_date_string_pretty}

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

        # Store ain holder
        all_data[calculated_date_string_pretty] = end_dates_dict
        #print(end_dates_dict)


# Sort all dates and loop through them to populate the csv to have all data


# Open template outpout and append to the completion dates...
# This is either the running current status, or a new template with a lies to tasks
template_fname = os.path.join(DNAME_OUT, base_template)
output_fname = os.path.join(DNAME_OUT, todays_date + '.csv')  # file saved with this current (intermediate) updated

# Open the streams
t = open(template_fname)
o = open(output_fname, 'w')

reader = csv.reader(t)
writer = csv.writer(o)

print('Writing output to ', output_fname)


# For each line in the template, add the dates from the dictionaries
for line in reader:
    #print("line in: ", line)
    for this_date in sorted(all_data.keys()):
        end_dates_dict = all_data[this_date]
        if line[1] in end_dates_dict:
            line.append(end_dates_dict[line[1]])
        else:
            line.append(' ') # make placeholder if dat is missing this week...


    writer.writerow(line)
    #print('line out: ', line)

# close things
t.close()
o.close()

# copy to current
current_fname = os.path.join(DNAME_OUT, fname_out)  # final output name "current"
print('Done writing, copying to ', current_fname)
copy(output_fname, current_fname)

print('DONE')
