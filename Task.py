'''
Task - a class to hold the functionality of a Task

'''

import datetime
import csv
import os
import os.path

#################################################
## Task  - a holder for a task
#################################################
class Task:

    # COnstructor - need hierarchical task number, name, enddate, subtasks, end date
    def __init__(self, name, task_number, enddate=None, hierarchical_task_name=None):
        self.name = name
        self.task_number = task_number
        self.enddate = enddate
        self.task_level = len(task_number.split('.'))
        self.hierarchical_task_name = hierarchical_task_name

    def get_task_level_parts(self):
        return self.task_number.split('.')

    def get_space(self):
        return self.get_level_value(1)

    def get_project(self):
        return self.get_cumulative_level_value(2)

    def get_list(self):
        return self.get_cumulative_level_value(3)

    def get_task(self):
        return self.get_cumulative_level_value(4)
    
    def get_subtask(self):
        return self.get_cumulative_level_value(5)
        
    def get_cumulative_level_value(self, level):
        if level > self.task_level:
            return None
        else:
            return ".".join(self.get_task_level_parts()[:level])

    def get_individual_level_value(self, level):
        if level > self.task_level:
            return None
        else:
            return self.get_task_level_parts()[level-1]

    def get_parent_number(self):
        if self.task_level <= 1:
            return None
        else:
            return ".".join(self.get_task_level_parts()[:self.task_level-1])
    

#################################################
## Task List 
#################################################
# A dictionary of tasks.  Can add and remove tasks and parent task enddates are updated...
class TaskList:
    def __init__(self):
        self.tasks = {}
        self.task_numbers = []

    # Make iterable behavior (do it this way instead of just returning the iter of self.tasks to ensure that we can iterate in order)
    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        if self.counter < len(self.task_numbers):
            x = self.tasks[self.task_numbers[self.counter]]
            self.counter += 1
            return x
        else:
            raise StopIteration

    # Contaisn so can check if we have a task:
    def __contains__(self, key):
        if isinstance(key, Task):
            return key.task_number in self.task_numbers
        else:
            return key in self.task_numbers

    # Add task to list
    def add(self, task):
        if not isinstance(task, Task):
            print('Input to add_task is not an instance of class Task! - not adding.')
            return
        
        # Check to see if the task already exists
        if task in self.tasks:
            print('Task is already in the list.  Do you wnt to update it instead?')
            return

        # Add the task
        self.tasks[task.task_number] = task
        self.task_numbers.append(task.task_number)

        # Sort the task numbers
        self.task_numbers.sort(key=lambda x: self.get_comparable_task_number_representation(x))
        #self.sort_task_numbers()

        # If this doesn't have an enddate, then make one from children...
        if not task.enddate:
            the_children = self.get_immediate_children_of_task(task)
            max_enddate = None
            if len(the_children) > 0:
                for child in the_children:
                    if child.enddate is not None:
                        if max_enddate is None or child.enddate > max_enddate:
                            max_enddate = child.enddate
                #max_enddate = max(self.get_immediate_children_of_task(task), key=lambda x: x.enddate).enddate
            if max_enddate is not None:
                task.enddate = max_enddate
            #
            # max_enddate = 0
            #for child_task in self.get_immediate_children_of_task(task):
                


        # If still nothign, we are doe
        if not task.enddate:
            return

        # Update the end dates of all parents
        the_parent = self.get_parent_of_task(task)
        while the_parent is not None:
            if the_parent.enddate:
                if task.enddate > the_parent.enddate:
                    the_parent.enddate = task.enddate
                    the_parent = self.get_parent_of_task(the_parent)
                else:
                    the_parent = None
            else:
                the_parent.enddate = task.enddate

        # Update the enddate, 

    # Sort task numbers (they are strings so, 10 would be before 2...  need to transform...)
    def sort_task_numbers(self):
        task_number_representation = []
        for task_number in self.task_numbers:
            task_number_split =  list(map(int, task_number.split('.')))
            this_representation = 0
            for ind, val in enumerate(task_number_split):
                this_representation += 10**(12-3*ind) * task_number_split[ind]
            #this_representation = 1e12*task_number_split[0] + 1e9*task_number_split[1] + 1e6*task_number_split[2] + 1e3*task_number_split[3]
            # if len(task_number_split) > 4:
            #     this_representation += task_number_split[4]
            # task_number_representation.append(this_representation)
        
        # now sort, based on this representation
        inds = range(len(task_number_representation))
        sorted_inds = [x for _,x in sorted(zip(task_number_representation, inds))]

        self.task_numbers = [self.task_numbers[i] for i in sorted_inds]

    # Get a comparable task number prepresentation
    # Note that htis is limited to 999 tasks per parent per level (i think this should be ok)
    def get_comparable_task_number_representation(self, task_number):
        task_number_split =  list(map(int, task_number.split('.')))
        this_representation = 0
        for ind, val in enumerate(task_number_split):
            this_representation += 10**(12-3*ind) * task_number_split[ind]

        return this_representation

    # Get task
    def get_task(self, task_number):
        if task_number in self.tasks:
            return self.tasks[task_number]
        else:
            return None

    # Get parent task
    def get_parent_of_task(self, task):
        return self.get_task(task.get_parent_number())

    # Get immediate child tasks of this one
    def get_immediate_children_of_task(self, task):
        output_list = []

        for test_task in self.tasks.values():
            if test_task.get_parent_number() == task.task_number:
                output_list.append(test_task)
        
        return output_list

    # Get all Child tasks of this one
    def get_all_children_of_task(self, task):
        output_list = []

        for test_task in self.tasks:
            if test_task.task_number.startswith(task_number):
                output_list.append(test_task)
        
        return output_list
    
    # Update the enddate bu looking at max enddate of all children
    def update_enddate_of_task(self, task):
        for test_task in self.get_all_children_of_task(task):
            if task.enddate:
                if test_task.enddate > task.enddate:
                    task.enddate = test_task.enddate
            else:
                task.enddate = test_task.enddate

    # Get all parents of this task
    def get_all_parents_of_task(self, task):
        output_list = []

        the_parent = self.tasks[task.get_parent_number()]
        while the_parent is not None:
            output_list.append(the_parent)
            the_parent = self.tasks[the_parent.get_parent_number()]

    # Get all task numbers in this TaskList
    def get_all_task_numbers(self):
        return self.task_numbers

#################################################
## Task List Array - a group of task lists...
#################################################
class TaskListArray:
    def __init__(self):
        self.task_list_dict = {}
        self.date_calculated_list = []
        self.task_numbers = []
        self.global_task_list = TaskList()

    # Make iterable behavior (do it this way instead of just returning the iter of self.tasks to ensure that we can iterate in order)
    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        if self.counter < len(self.date_calculated_list):
            x = self.task_list_dict[self.date_calculated_list[self.counter]]
            self.counter += 1
            return x
        else:
            raise StopIteration

    # Contaisn so can check if we have a task:
    def __contains__(self, key):
        return key in self.date_calculated_list

    # String representation
    def __str__(self):
        this_str = "Task Number \t Task Name \t Date Calculated \n \t \t \t"
        for date_calculated in self.date_calculated_list:
            this_str += "\t" + date_calculated
        
        for task in self.global_task_list:
            this_str += "\n %s \t\t %s " % (task.task_number, task.name)
            for date_calculated in self.date_calculated_list:
                this_str += "\t"
                if task in self.task_list_dict[date_calculated]:
                    this_str += str(self.task_list_dict[date_calculated].get_task(task.task_number).enddate.strftime('%m/%d/%Y'))
                else:
                    this_str += "\t"

        return this_str

    def output_to_csv(self, fname_out):
            #writer = csv.writer(csvfile)

        this_str = ",Date Calculated "
        for date_calculated in self.date_calculated_list:
            this_str += "," + date_calculated
        
        for task in self.global_task_list:
            this_str += "\n %s,%s " % (task.task_number, task.name.replace(',', ' -'))
            for date_calculated in self.date_calculated_list:
                this_str += ","
                if task in self.task_list_dict[date_calculated] and self.task_list_dict[date_calculated].get_task(task.task_number).enddate is not None:

                    this_str += str(self.task_list_dict[date_calculated].get_task(task.task_number).enddate.strftime('%m/%d/%Y'))
                else:
                    this_str += "" # "/t" just add this tab for spacing

        with open(fname_out, 'w') as csvfile:
            csvfile.write(this_str)

        print("OUTPUT TO CSV FILE: ", fname_out)
        #print(this_str)

    # Add - 
    # Maintain global task list of all task nubmers...
    def add(self, task_list, date_calculated):
        if not isinstance(task_list, TaskList):
            print('Input to TaskListArray.add is not an instance of class TaskList! - not adding.')
            return
        
        # add to dict
        self.task_list_dict[date_calculated] = task_list
        self.date_calculated_list.append(date_calculated)
        self.date_calculated_list.sort()

        # Update list of all tasks
        for task_number in task_list.get_all_task_numbers():
            if task_number not in self.task_numbers:
                self.task_numbers.append(task_number)
                self.global_task_list.add(task_list.get_task(task_number))
            # Verify that the task number and task name are the same for any list that is added...
            task_name_new = task_list.get_task(task_number).name
            task_name_old = self.global_task_list.get_task(task_number).name
            if task_name_new != task_name_old:
                print('ERROR: new and old task names do not match for task number {task_number}!!!: {task_name_new} <==> {task_name_old}')

            hierarchical_task_name_new = task_list.get_task(task_number).hierarchical_task_name
            hierarchical_task_name_old = self.global_task_list.get_task(task_number).hierarchical_task_name
            if hierarchical_task_name_new != hierarchical_task_name_old:
                print('ERROR: new and old hierarchical task names do not match for task number {task_number}!!!: {hierarchical_task_name_new} <==> {hierarchical_task_name_old}')

        self.task_numbers.sort()



############################################
# MAIN ENTRYPOINT (for testing)
############################################
if __name__ == "__main__":
    a = TaskList()
    a.add(Task("Test 1.1.1", "1.1.1", datetime.datetime(2019, 1, 1)))
    a.add(Task("Test 1.1.2", "1.1.2", datetime.datetime(2019, 2, 1)))
    a.add(Task("Test 1.1", "1.1"))

    for task in a:
        print('Task: ', task.task_number, ' - enddate ', task.enddate)

    print("Adding subtask")
    a.add(Task("Test 1.1.3", "1.1.3", datetime.datetime(2019, 1, 3)))
    for task in a:
        print('Task: ', task.task_number, ' - enddate ', task.enddate)


    b = TaskList()
    b.add(Task("Test 1.1.1", "1.1.1", datetime.datetime(2019, 1, 1)))
    b.add(Task("Test 1.1.3", "1.1.3", datetime.datetime(2019, 1, 2)))
    b.add(Task("Test 1.1.4", "1.1.4", datetime.datetime(2019, 1, 4)))
    b.add(Task("Test 1.1", "1.1"))

    c = TaskListArray()
    c.add(a, '2/1/2019')
    c.add(b, '3/1/2019')

    print(c)
    c.output_to_csv('test.csv')