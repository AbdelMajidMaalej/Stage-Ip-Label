#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import subprocess
import csv


# In[2]:


new_directory_path = "C:/Users/ASUS/Documents/Stage"

os.chdir(new_directory_path)

# Verify the new current working directory
current_directory = os.getcwd()
print("Current working directory:", current_directory)


# In[3]:


def run_locust(url): 
    command = f"locust -f my_script.py --headless --csv=example -u 1000 --run-time 5s --host={url}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        print(f"Error executing Locust: {error.decode(errors='replace')}")
        return None

    try:
        decoded_output = output.decode('utf-8')
    except UnicodeDecodeError:
        decoded_output = output.decode('latin-1')

    return decoded_output


# In[9]:


def set_reward():
    csv_file_path = "example_stats.csv"

    with open(csv_file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        performance_reward = 0   
        for row in reader:
                # Access values by header name
                requestCount = row['Request Count']
                failureCount = row['Failure Count']
                averageResponseTime = row['Average Response Time']
                requestPerSec = row['Requests/s']
                FailuresPerSec = row['Failures/s']
                try:
                    requestCount = int(requestCount)
                    failureCount = int(failureCount)
                    averageResponseTime = float(averageResponseTime)
                    requestPerSec = float(requestPerSec)
                    FailuresPerSec = float(FailuresPerSec)
                    if requestCount != 0:
                        performance_reward -= (failureCount / requestCount)
                    else:
                        performance_reward -= 0.5
                    performance_reward -= averageResponseTime * 0.0001
                    performance_reward += requestPerSec * 0.1
                    performance_reward -= FailuresPerSec * 0.1
                except ValueError:
                    performance_reward = -100
        print(performance_reward)
    try:
            os.remove("example_exceptions.csv")
            os.remove("example_failures.csv")
            os.remove("example_stats.csv")
            os.remove("example_stats_history.csv")
    except OSError as e:
            print(f"Error deleting file: {e}")
    return performance_reward


# In[10]:


def get_reward(website_url):
    # Run Locust and capture the output
    locust_output = run_locust(website_url)
    reward = set_reward()
    return reward



# In[ ]:




