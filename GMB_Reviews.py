#Read the Readme file

import pandas as pd
import requests
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient import sample_tools
from googleapiclient.http import build_http
import json
from pathlib import Path
import re
import unicodecsv as csv
from glob2 import glob

directory = "Set your directory"
SCOPES = ["https://www.googleapis.com/auth/business.manage"]


# specify the folder path containing the JSON files
folder_path = directory

# use glob to find all JSON files in the folder
json_files = glob(folder_path + '*.json')

""""""""""""""""""""""""""""""""
"Generate Access Token"
""""""""""""""""""""""""""""""""

creds = None
if Path("token.json").exists():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())
        
""""""""""""""""""""""""""""""""
"Using build, generate account name and locations attached to the locations"
""""""""""""""""""""""""""""""""

with build("mybusinessaccountmanagement", "v1", credentials=creds) as service:
    account_list = service.accounts().list().execute()
    account_name = account_list["accounts"][0]["name"]
    service.close()



with build("mybusinessbusinessinformation", "v1", credentials=creds) as service:
    loc = service.accounts().locations().list(parent = account_name, readMask="Name,title").execute()
    #print(loc)
    a = list(loc.values())
    location_list =[]

    for i in range(len(a[0])):
        x=list(a[0][i].values())
        location_list.append(x)
    
    service.close()
    
""""""""""""""""""""""""""""""""
"Writing the api data to json files."
"Each request creates a separate numbered file which can later be combined"
""""""""""""""""""""""""""""""""

def write_json_to_file(directory, filename, data, k):
    try:
        file_name = f"{filename}.json"
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)
        print(f"{file_name} saved successfully!")
    except (FileNotFoundError, IOError) as e:
        print(f"Error saving {file_name}: {str(e)}")
    except Exception as e:
        print(f"Unknown error occurred while saving {file_name}: {str(e)}")
        
""""""""""""""""""""""""""""""""
"Iterating through the locations to get the reviews"
""""""""""""""""""""""""""""""""        
        

def get_reviews(account, location, title, page_size=50, page_token=None, order_by=None):
    credentials = creds
    headers = {"Authorization": f"Bearer {credentials.token}"}    
    url = f"https://mybusiness.googleapis.com/v4/accounts/{account_name}/{location}/reviews"
    api_req = requests.get(url, headers=headers)
    review_data = api_req.json()
    count = review_data.get('totalReviewCount')
    if count is None:
        count = 0
    filename = current_title +".json"
    
    k=10  
    i=50
    if count>i:
        write_json_to_file(directory,current_title, review_data,k)
        nextpagetoken=review_data.get('nextPageToken')
        left = count-i
        for k in range((i+left-1)//i):
             url = f"https://mybusiness.googleapis.com/v4/accounts/{account_name}/{location}/reviews?pageToken={nextpagetoken}"
             api_req = requests.get(url, headers=headers)
             iter_data = api_req.json()
             filename= current_title + str(k)
             write_json_to_file(directory,filename, iter_data,k)
    else:
        write_json_to_file(directory,current_title, review_data,k)
    return print(api_req)

for i in range(len(location_list)):
    current_loc=location_list[i][0]
    current_title= location_list[i][1]
    get_reviews(account_name, current_loc, current_title)
    
""""""""""""""""""""""""""""""""
"Adding Filename which is location title as a column "
"and concatenate all fields from api result"
""""""""""""""""""""""""""""""""
# create an empty list to store the DataFrames
dfs = []

# iterate over the JSON files and read them into DataFrames
for file in json_files:
    with open(file, 'r') as f:
        data = json.load(f)
        if 'reviews' in data:
            df = pd.json_normalize(data['reviews'])
            
            # extract the filename from the file path
            col_name = os.path.basename(file)
            
            # create a new column with the filename
            df['Location'] = col_name
            dfs.append(df)
         

# concatenate all DataFrames into a single DataFrame
result = pd.concat(dfs, ignore_index=True, sort=False)

""""""""""""""""""""""""""""""""
"Final Step: Converting the dataframe to csv with exception handling"
""""""""""""""""""""""""""""""""

try:
    result.to_csv('GoogleReviews.csv', index=False)
    print("GoogleReviews saved successfully !")
except Exception as e:
    print("Couldn't save the file because of :" + str(e))
