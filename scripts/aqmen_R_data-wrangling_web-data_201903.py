# -*- coding: utf-8 -*-

# 
# AQMEN (Data Science for Social Research)
# http://www.aqmen.ac.uk/
#
# 
# Data Wrangling: Organising and Enabling Data
# 
# R and Python Workshop (March 2019)
# 
# A three day hands-on workshop led by Dr Diarmuid McDonnell and Professor Vernon Gayle, University of Edinburgh.
# 
# 

# 5. Harvesting Web-based Data [ACT005] #

print("Hello World!")

# TASK: highlight the above code and execute by pressing Ctrl + Enter.

'''
Welcome to Python!

You'll notice that Spyder IDE is quite similar to RStudio.

Also notice how we've enclosed all of this text in three single quotes.
'''

# Here is a single line comment.

# This activity is a very rapid introduction to Python for harvesting data from the web.
# There are multiple programming languages (including R) that can be used to collect
# web data. We feel that Python offers an array of packages
# and functions that make harvesting web data simple and powerful, but the choice is yours.

# We demonstrate the following skills in this workshop:
#   1. Installing and loading packages in Python
#   2. Setting up project folders
#   3. Downloading files from the web
#   4. Harvesting information from websites
#   5. Exporting web data to familiar file formats (e.g. csv, txt) 
#   6. Connecting to online databases (APIs) and requesting information


################################################################################################


################################################################################################



# 5.1 Installing and loading packages

# 5.1.1 Installing packages on your machine

# This is done a little differently in Python: instead of installing directly in Python,
# we need to use the command prompt/terminal on your machine.

# The tutor will now demonstrate how this is achieved.


# 5.1.2 Loading packages

# We import (load) modules (packages) as follows:

try:
    import json # module for handling json files
    import csv # module for handling csv files
    import requests # module for requesting urls
    import os # module for performing operating system tasks
    import pandas as pd # module for data wrangling
    from bs4 import BeautifulSoup as soup # module for parsing web pages
    print("Successfully imported modules")
except:
    print("Did not import one or more modules!")
    
# QUESTION: what do you think the try, except block does?    


################################################################################################


################################################################################################


# 5.2 Setting up project folders

# Let's use the same folders we created earlier in the workshops

# Define paths

wd = "C:/Users/mcdonndz-local/Desktop/data-wrangling-201903" # define the working directory
data_raw = wd + '/' + 'data_raw' # raw data directory

print(wd) # print the string identifying the workshop working directory
print(data_raw) # print the string identifying the raw data directory

# We can enclose strings in single or double quotes (just like R).


################################################################################################


################################################################################################


# 5.3. Downloading files from the web

# The Charity Commission for Northern Ireland (CCNI) releases csv files of
# various data sets relating to charities in its jurisdiction.

# We could just visit the website and download the files manually, so why would a 
# Python script be an improvement?
#   - quicker (once the script has been written) 
#   - reproducible
#   - automatable 
#   - less prone to error

# The final two reasons are the most important: charity records, like a lot of administrative
# data sets, are continuously updated. This means that observations for certain organisations
# can disappear over time. A script that rountinely and accurately downloads regular
# snapshots of charity data would be a valuable data collection tool.

# Enough talk, more action:

# Define the urls where the datasets can be downloaded

regurl = "https://www.charitycommissionni.org.uk/umbraco/api/charityApi/ExportSearchResultsToCsv/?pageNumber=1"
trusteeurl = "https://www.charitycommissionni.org.uk/media/1144/20180327-register-of-removed-trustees.xls"

# Download Register

r = requests.get(regurl, allow_redirects=True) # request the url
print(r.status_code, r.headers) # print the metadata behind the request to see if it was successful
# A status code of 200 is what we are looking for.

# Write the r.content to a file on Dropbox
print(type(r.content)) # Python object containing the csv file

outputfile = data_raw + "/ni_charityregister_201903.csv" # create an object storing the path and file name of the csv
print(outputfile) # display this path to the console

with open(outputfile, 'wb') as f: # with the output file open in "write binary" mode, and giving it a shorter name (f)
    f.write(r.content) # write the contents of the r.content object to the file
    f.close() # close the file
    
 # Go check the "data_raw" folder to see if the file was downloaded successfully.   

# TASK: download the disqualified trustee file to the "data_raw" folder. HINT: the location
# of the file is contained in the "trusteeurl" object.


################################################################################################


################################################################################################
 
 
# 5.4 Harvesting information from websites
 
# Downloading files from the web is relatively unproblematic. It is a different scenario if
# we want to download information contained in the text of the webpage itself.
 
# For this we need a different approach: we need to parse the contents of a webpage, find the
# information we are interested in, store it in Python objects, and write this objects to a file.
 
# This sounds a bit abstract, so let's get stuck in to an example.
 
# Staying with Northern Ireland, it would be good to have a list of trustees for each charity.
# This information is not contained in any data download file but it can be viewed online:
# .e.g. https://www.charitycommissionni.org.uk/charity-details/?regId=100003&subId=0
 
 
# Define files
 
inputfile = data_raw + "/ni_charityregister_201903.csv" # use the charity register as our input file
outputfile = data_raw + "/ni_trustee_data_201903.csv" # file where the web-scrape results will be stored

# Delete output file if already exists

try:
    os.remove(outputfile)
except OSError:
    pass # this means continue in the event the code in the "try" block doesn't execute

# Create a data frame containing the input file
    
pd.set_option('precision', 0) # change the default precision option for data frames

with open(inputfile, 'rb') as f:
	df = pd.read_csv(f)
	print(df.dtypes)
    
# QUESTION: what is the above block of code doing?

# Create a list of charity numbers that we can search for on the Regulator's web portal

df.reset_index(inplace=True) 
df.set_index(['Reg charity number'], inplace=True) # set charity number as unique id of an observation

regno_list = df.index.values.tolist() # create a list object containing charity numbers
print(regno_list)

# Write variable names to the output file

varnames = ['Charity Number', 'Trustee Name'] # create a list of variable names

with open(outputfile, 'a') as f:
	writer = csv.writer(f, varnames)
	writer.writerow(varnames) # write the variable names to the first row of the output file
    
# Begin searching for charity records on the web portal
    
for ccnum in regno_list[0:20]: # for the first 20 charity numbers contained in regno_list
    
    # Construct the web portal address of a charity
    
    webadd = 'https://www.charitycommissionni.org.uk/charity-details/?regid=' + str(ccnum) +'&subid=0'
    
    rorg = requests.get(webadd, allow_redirects=True) # request a charity's web page
    print(rorg.status_code, rorg.headers) # check if the page was requested successfully
    
    html_org = rorg.text # Get the text elements of the page
    soup_org = soup(html_org, 'html.parser') # Parse the text as a Beautiful Soup object
    
    if not soup_org.find('div', {"class": "status removed"}): # if the charity isn't removed from the Register then proceed with scraping trustee info
        trustees = soup_org.find_all('td') # find the contents of the trustee table (i.e. the "td" tags)
        print(trustees) # print the results of this search
        
        # It looks like we have what we need; now let's extract the trustee name from table
        
        trustee = list(map(lambda x : x.text, trustees)) # extract trustee name from within the "td" tags
        print(trustee)
    
        trustee_dict = {"ccnum": ccnum, "trustee": trustee} # store downloaded data as a dictionary
        df_csv = pd.DataFrame(trustee_dict) # convert the dictionary to a data frame
        print(df_csv) # print the contents of the data frame
		
        with open(outputfile, 'a') as f: # write the results of the web scrape to the output file
            df_csv.to_csv(f, header=False, index=False)
    else: # no trustee information available
        print('\r')
        print('No trustee information available for this charity | regno: ' + str(ccnum))
        print('\r')
    
print("Finished searching for trustee information.")

# And there we have it: a simple web-scraper for collecting trustee names from the Regulator's
# website.

# We've covered quite a lot so take a bit of time to reflect on what the above code does, how it
# parses web pages, how it stores results in various data structures (e.g. lists, dictionaries etc).

# We don't have the time to cover data structures or HTML in more detail but we strongly advise
# that you become familiar with these topics if you wish to conduct your own harvesting of
# web data.
    

################################################################################################


################################################################################################


# 5.5 Connecting to online databases (APIs) and requesting information

# Our final task is to collect information stored in a tabular structure in an online database.

# APIs provide a means of communicating with an online database in much the same way as 
# requesting a web page (i.e. through urls).

# The rules (or grammar) for making an API request are a little bit different than those
# for connecting to web pages.

# For this example we request open data on U.K. policing from the Police API:
# data.police.uk - [https://data.police.uk/]


# Define paths

wd = "C:/Users/mcdonndz-local/Desktop/data-wrangling-201903" # define the working directory
data_raw = wd + '/' + 'data_raw' # raw data directory

print(wd) # print the string identifying the workshop working directory
print(data_raw) # print the string identifying the raw data directory

# Define API endpoints

# An endpoint is an identifier for a table or data resource. Different data sets have
# different endpoints, and this allows you to customise your requests.

base = "https://data.police.uk/api/" # the base of every API url
forces = "forces" # list of police forces in the UK
location = "neighbourhoods" # List of neighbourhoods for a force
soff = "people" # list of senior officers for a force

# Request information from the API #

# Request a list of police forces

r = requests.get(base+forces)
print(r.status_code, r.headers) # print the metadata behind the request to see if it was successful

print(r.content) # view the results of the request; list of dictionaries

fdata = json.loads(r.content) # convert result to json format
print(type(fdata)) # list object

# Export the json data to a file

forces_file = data_raw + "/" + "forces.json"

with open(forces_file, 'w') as f:
    json.dump(fdata, f)

# TASK: check if the json file was saved in the "data_raw" directory.
    
# Import the forces data back into Python

with open(forces_file, 'r') as f:
	fdata = json.load(f)
    
print(fdata)   

# Extract force id from the Python object

fid_list = [] # create a blank list

for el in fdata: # for each element/row in the forces object
    print(el)
    fid = el["id"] # extract the value of the "id" field
    fid_list.append(fid) # append this value to the blank list
    
print(fid_list)

# Use the list of force ids to search for senior officers

for fid in fid_list: # search for the ids in the list
    print(fid)
    r = requests.get(base+forces+"/"+fid+"/"+soff)
    print(r.status_code, r.headers) # print the metadata behind the request to see if it was successful
    
    print(r.content) # lots of blank results: the endpoints exist but do not contain senior officer information for some forces
    
# If you find you are getting status code = 404 then don't be alarmed. While this means you
# were unable to request the API endpoint, it is likely due to the rate limit. This is the limit
# on the number of requests you can send to an API in a given timeframe.
    
    
# Final Thoughts #

# Some things to consider with harvesting data from the web:
    # 1. You should still adhere to ethical research principles and practices.
    # 2. Make sure you comply with the restrictions arounf the use of certain information e.g. email addresses, phone numbers.
    # 3. The old ways can be best i.e. requesting data from a human.
    

# EXERCISE:
# Free play time: consult the Police API documentation and construct your own API searches.
# [https://data.police.uk/docs/]


### END OF ACTIVITY FIVE [ACT005] ###    