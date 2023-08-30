#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By


# In[ ]:


def get_form_details(form):
    """Returns the HTML details of a form,
    including action, method and list of form controls (inputs, etc)"""
    details = {}
    # get the form action (requested URL)
    action = form.get_attribute("action").lower()
    # get the form method (POST, GET, DELETE, etc)
    # if not specified, GET is the default in HTML
    method = form.get_attribute("method")
    method = method.lower() if method else "get" 
    # get all form inputs
    inputs = []
    for input_tag in form.find_elements(By.CSS_SELECTOR, "input"):
        # get type of input form control
        input_type = input_tag.get_attribute("type") or "text"
        # get name attribute
        input_name = input_tag.get_attribute("name")
        # get the default value of that input tag
        input_value = input_tag.get_attribute("value")
        input_value = input_value.lower() if input_value else "" 
        input_required = input_tag.get_attribute("required") is not None
        # add everything to that list
        inputs.append({"type": input_type, "name": input_name, "value": input_value , "element" : input_tag, "required": input_required})
    for select in form.find_elements(By.CSS_SELECTOR, "select"):
        # get the name attribute
        select_name = select.get_attribute("name")
        # set the type as select
        select_type = "select"
        select_options = []
        select_required = select.get_attribute("required") is not None 
        # the default select value
        select_default_value = ""
        # iterate over options and get the value of each
        for select_option in form.find_elements(By.CSS_SELECTOR, "option"):
            # get the option value used to submit the form
            option_value = select_option.get_attribute("value")
            
            if option_value:
                select_options.append(option_value)
                if select_option.get_attribute("selected"):
                    # if 'selected' attribute is set, set this option as default    
                    select_default_value = option_value
        if not select_default_value and select_options:
            # if the default is not set, and there are options, take the first option as default
            select_default_value = select_options[0]
        # add the select to the inputs list
        inputs.append({"type": select_type, "name": select_name, "values": select_options, "value": select_default_value, "element" : select_option, "required": select_required})
    for textarea in form.find_elements(By.CSS_SELECTOR, "textarea"):
        # get the name attribute
        textarea_name = textarea.get_attribute("name")
        # set the type as textarea
        textarea_required = textarea.get_attribute("required") is not None 
        textarea_type = "textarea"
        # get the textarea value
        textarea_value = textarea.get_attribute("value")
        textarea_value = input_value.lower() if input_value else ""
        # add the textarea to the inputs list
        inputs.append({"type": textarea_type, "name": textarea_name, "value": textarea_value, "element" : textarea, "required": textarea_required})
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details


# In[ ]:


def submit_form(driver,form):
    form_details = get_form_details(form)
    print("="*50, f"form", "="*50)
    print(form_details)
    # the data body we want to submit
    for input_tag in form_details["inputs"]:
        try:
            if input_tag["type"] == "select":
                # Create a Select object for the <select> element
                select = Select(input_tag["element"])
                # Choose an option by value
                select.select_by_value(input_tag["values"][-1])  # Replace with the desired option value
          
            elif input_tag["type"] == "email":
                # all others except submit, prompt the user to set it
                input_tag["element"].send_keys("iplabeltest@gmail.com")
            elif input_tag["type"] == "text":
                # all others except submit, prompt the user to set it
                input_tag["element"].send_keys("Hello")
            elif input_tag["type"] == "checkbox":
                if input_tag["required"] == "True":
                    if not input_tag["element"].is_selected():
                        input_tag["element"].click()
            elif input_tag["type"] == "radio":
                try:
                    input_tag["element"].click()
                    print("click")
                except:
                    try:
                        print("ElementNotInteractableException1")
                        parent_element = input_tag["element"].find_element(By.XPATH, "..")
                        parent_element.click()
                    except ElementNotInteractableException:
                        print("ElementNotInteractableException2")
            elif input_tag["type"] == "password":
                # all others except submit, prompt the user to set it
                input_tag["element"].send_keys("IPLABEL2023")
        except ElementNotInteractableException:
            pass 
        # Submit the form based on the form method
        form.submit()

