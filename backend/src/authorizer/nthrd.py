import threading
import schedule
import time

lst = ['Monday', 'Tuesday', 'Wednesday', 'Saturday', 'Sunday']
def print_and_pop(arr):
    print(arr)


schedule.every(1).seconds.do(print_and_pop, lst)
inp = "Hello, World"

def push(arr):
    arr.append("pushing")


# Define a filter function to select job1
filter_1 = lambda job: job.name == 'run'
filter_2 = lambda job: job.name == 'push'



def run():
    while True:
        schedule.run_pending()
        time.sleep(1)

thread_2 = threading.Thread(target=run)
thread_2.start()
print('here from main')
time.sleep(10)
print('goood looks')
while True:
    time.sleep(5)
    lst.append('yesss')

print('over')
thread_2.join()

