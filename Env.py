#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By


# In[2]:


from gym import Env
from gym import spaces
import numpy as np


# In[3]:


from Reward import get_reward
from Form import submit_form
import random


# In[7]:


class Agent(Env):
    def __init__(self,dic,tabs):
        super(Agent, self).__init__()
        # Define observation space
        self.observation_space = spaces.Discrete(len(tabs))
        
        # Define a dictionary to map each state to its corresponding action space
        self.state_action_spaces = { 
            key : spaces.Discrete(value)  for key, value in dic.items()
                                   }
        
        # Initialize other environment-specific variables here
        self.state = random.randint(0,self.observation_space.n-1)
        self.all_elements = tabs
        self.urls_visited = []
        self.driver = self.get_driver(tabs[self.state]["page"])

    def reset(self):
        # Reset the environment to its initial state
        self.urls_visited = []
        self.state = random.randint(0,self.observation_space.n-1)
        self.driver.get(self.all_elements[self.state]["page"])
        return self.state

    def step(self, action, state):
        #Get the random action
        element = self.all_elements[state]["page_elements"][action]
        current_url, reward = self.execute_element(element,action, state)
        current_url = current_url.split("#")[0]
        new_observation = 0
        info = {}
        for i,page in enumerate(self.all_elements):
            if current_url == page["page"]:
                new_observation = i
                done = self.is_episode_done(current_url)
                break
            else:
                done = True
                new_observation = -1
            if reward == 100 or new_observation==state:
                done = True
            if done:
                info = {"scenario" : self.urls_visited}
        return new_observation, reward, done, info

    def get_current_action_space(self):
        current_state = self.observation_space.sample()  # Replace with actual current state
        return self.state_action_spaces[current_state]
    
    def is_episode_done(self,url):
        if len(self.urls_visited) >= 10:
            return True
        else:
            url = url.split('#')[0]
            if url in self.urls_visited:
                return True
            else:
                return False
        
    def execute_element(self, element, action, state):
        if element["type"]=="button":
            try:
                button = self.driver.find_element(By.XPATH, element["xPath"])
                print("button")
                button.click()
                reward = get_reward(self.driver.current_url) - 0.1
            except Exception as error:
                # Handle the exception
                error_type = type(error).__name__  # Get the exception type as a string
                error_message = str(error)          # Get the error message as a string
                if error_type == "NoSuchElementException":
                    reward = 100
                else:
                    reward = 0
                    print("Erreur Type: " + error_type)
        elif element["type"]=="form":
            try:
                form = self.driver.find_element(By.XPATH, element["xPath"])
                print("form")
                submit_form(self.driver,form)
                reward = get_reward(self.driver.current_url) - 0.1
            except Exception as error:
                # Handle the exception
                error_type = type(error).__name__  # Get the exception type as a string
                error_message = str(error)          # Get the error message as a string
                print("Erreur Type: " + error_type)
                
                reward = 0
        elif element["type"]=="input":
            try:
                input_element = self.driver.find_element(By.XPATH, element["xPath"])
                print("input")
                text_to_write = "Hello"
                input_element.send_keys(text_to_write)
                reward = get_reward(self.driver.current_url) - 0.1     
            except Exception as error:            
                # Handle the exception
                error_type = type(error).__name__  # Get the exception type as a string
                error_message = str(error)          # Get the error message as a string
                print("Erreur Type: " + error_type)
                reward = 0
        current_url = self.driver.current_url
        print(current_url)
        self.urls_visited.append({"state":state, "action":action, "reward": reward})
        return current_url,reward
        
    def get_driver(self,url):
            chrome_options = Options()
            service = Service(executable_path='C:\Program Files (x86)\chromedriver.exe')
            chrome_options.binary_location = 'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Specify the path to the Chrome browser executable if needed
            #chrome_options.add_argument('--headless')  # Run Chrome in headless mode
            print(url)
            # Set up Chrome WebDriver with the local ChromeDriver executable
            driver = webdriver.Chrome(options=chrome_options, service=service)
            driver.get(url)
            return driver
        
        
        


# In[ ]:




