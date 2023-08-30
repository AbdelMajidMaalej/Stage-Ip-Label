#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from collections import deque
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import codecs
import re
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_absolute_xpath(driver,element):
    # Generate the absolute XPath for the given element
    absolute_xpath = driver.execute_script(
        "function absoluteXPath(element) {"
        "   var comp, comps = [];"
        "   var parent = null;"
        "   var xpath = '';"
        "   var getPos = function(element) {"
        "       var position = 1, curNode;"
        "       if (element.nodeType == Node.ATTRIBUTE_NODE) {"
        "           return null;"
        "       }"
        "       for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {"
        "           if (curNode.nodeName == element.nodeName) {"
        "               ++position;"
        "           }"
        "       }"
        "       return position;"
        "   };"
        ""
        "   if (element instanceof Document) {"
        "       return '/';"
        "   }"
        ""
        "   for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {"
        "       comp = comps[comps.length] = {};"
        "       switch (element.nodeType) {"
        "           case Node.TEXT_NODE:"
        "               comp.name = 'text()';"
        "               break;"
        "           case Node.ATTRIBUTE_NODE:"
        "               comp.name = '@' + element.nodeName;"
        "               break;"
        "           case Node.PROCESSING_INSTRUCTION_NODE:"
        "               comp.name = 'processing-instruction()';"
        "               break;"
        "           case Node.COMMENT_NODE:"
        "               comp.name = 'comment()';"
        "               break;"
        "           case Node.ELEMENT_NODE:"
        "               comp.name = element.nodeName;"
        "               break;"
        "       }"
        "       comp.position = getPos(element);"
        "   }"
        ""
        "   for (var i = comps.length - 1; i >= 0; i--) {"
        "       comp = comps[i];"
        "       xpath += '/' + comp.name.toLowerCase();"
        "       if (comp.position !== null) {"
        "           xpath += '[' + comp.position + ']';"
        "       }"
        "   }"
        ""
        "   return xpath;"
        "}"
        "return absoluteXPath(arguments[0]);", element)
    
    return absolute_xpath

def get_page_elements(driver,url):
    driver.get(url)
    # Extract all URLs and navigation data
    anchor_elements = driver.find_elements(By.TAG_NAME, 'a')
    all_elements = [{"type":"button","element":element,"next":None, "xPath":None} for element in anchor_elements]
    """input_elements = driver.find_elements(By.CSS_SELECTOR, "input")"""
    form_elements = driver.find_elements(By.TAG_NAME, 'form')
    all_elements.extend([{"type":"form","element":element,"next":None, "xPath":None} for element in form_elements])
    """all_elements.extend([{"type":"input","element":element,"next":None, "xPath":None} for element in input_elements])"""
    return all_elements

def get_page(base_url,tabs,url,driver):
    index = None
    if url != None and base_url in url:
        exist = False
        url = url.split("#")[0]
        for page in tabs:
            if page["page"] == url:
                exist = True
                index = page["index"]
                break
                
        if exist:
            return page["index"],True
        else:
            # Execute JavaScript to open a new tab.
            script = f"window.open('{url}', '_blank');"
            driver.execute_script(script)
            index=len(tabs)-1
            tabs.append({"page":url,"index":index,"page_elements" : []})
            return index,False
    else:
        return index,False
        
    

def open_tab(base_url,url,tabs,element,driver):
        index, exist = get_page(base_url,tabs,url,driver)
        if index != None:
            # Switch to the new tab.
            new_tab_handle = driver.window_handles[index]
            driver.switch_to.window(new_tab_handle)
            element["next"] = driver.current_url
                

def next_element(base_url,tabs,driver,url,all_elements,element,index):
    new_tab_handle = driver.window_handles[index]
    driver.switch_to.window(new_tab_handle)
    absolute_xpath = get_absolute_xpath(driver,element["element"])
    l = len(all_elements)
    if element["type"]=="button":
        try:
            if "form" in absolute_xpath:
                all_elements.remove(element)
            else:
                url=element["element"].get_attribute('href')
                open_tab(base_url,url,tabs,element,driver)      
        except ElementNotInteractableException:
                all_elements.remove(element)
                print("deleted")
                print(len(all_elements) - l )
        except StaleElementReferenceException:
                print("Button : StaleElementReferenceException")
    elif element["type"]=="input":
        try:
            if "form" in absolute_xpath:
                all_elements.remove(old_element)
            else: 
                script = f"window.open('{driver.current_url}', '_blank');"
                driver.execute_script(script)
                # Switch to the new tab
                driver.switch_to.window(driver.window_handles[-1])
                text_to_write = "Hello"
                element = driver.find_element(By.XPATH, absolute_xpath)
                element.send_keys(text_to_write)
                url = driver.current_url
                element["next"] = url
                length = len(tabs)
                if length!=get_page(base_url,tabs,url,driver):
                    driver.close()
        except ElementNotInteractableException:
            all_elements.remove(element) 
        except StaleElementReferenceException:
            print("Input : StaleElementReferenceException") 
    element["xPath"] = absolute_xpath
        
        

def navigation_map(url):
    # Set up Chrome options
    chrome_options = Options()
    service = Service(executable_path='C:\Program Files (x86)\chromedriver.exe')
    chrome_options.binary_location = 'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Specify the path to the Chrome browser executable if needed
    #chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    chrome_options.add_argument('--page-load-timeout=60')
    #driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

    # Set up Chrome WebDriver with the local ChromeDriver executable
    driver = webdriver.Chrome(options=chrome_options, service=service)
    length = 0
    navigation_map = []
    tabs = [{"page": url,"index":0,"page_elements" : []}]
    base_url = url
    
    while length<len(tabs):
        print(length)
        start_time = time.time()
        driver.switch_to.window(driver.window_handles[length])
        if length == 0:
            current_url = url
        else:
            current_url = driver.current_url
        if current_url in navigation_map and current_url == "about:blank":
            del tabs[length]
            driver.close()     
        else:
            navigation_map.append(current_url)
            all_elements = get_page_elements(driver,current_url)
            for element in all_elements:
                next_element(base_url,tabs,driver,current_url,all_elements,element,length)
            tabs[length]["page_elements"] = all_elements
            end_time = time.time()
            execution_time = end_time - start_time
            print("------------------------")
            print(current_url)
            print(f" Time needed to extract all useful informations : {execution_time}")
            print("------------------------")
            length += 1
        
            
    for item in tabs:
        for element in item['page_elements']:
            if element['next'] == None:
                item['page_elements'].remove(element)
            elif element['xPath'] == None:
                item['page_elements'].remove(element) 
    dic = {
    index : len(page["page_elements"]) for index,page in enumerate(tabs)
}
    return tabs,dic

