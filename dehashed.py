#!/usr/bin/python3

import json
from typing import List
import requests
import argparse
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from time import sleep
import os
import sys

# Declare and assign terminal colors
RED="\033[1;31m"
BLUE="\033[1;34m"
RESET="\033[0m"
GREEN="\033[1;32m"
PURPLE="\033[1;35m"
ORANGE="\033[1;33m"
PINK="\033[1;35m"

# display banner
def display_banner():
     print(f"""{GREEN}
██████╗ ███████╗██╗  ██╗ █████╗ ███████╗██╗  ██╗███████╗██████╗
██╔══██╗██╔════╝██║  ██║██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗
██║  ██║█████╗  ███████║███████║███████╗███████║█████╗  ██║  ██║
██║  ██║██╔══╝  ██╔══██║██╔══██║╚════██║██╔══██║██╔══╝  ██║  ██║
██████╔╝███████╗██║  ██║██║  ██║███████║██║  ██║███████╗██████╔╝
╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═════╝

███████╗███╗   ██╗██╗   ██╗███╗   ███╗{ORANGE}by theblxckcicada{GREEN}
██╔════╝████╗  ██║██║   ██║████╗ ████║{PURPLE}on behalf of{GREEN}
█████╗  ██╔██╗ ██║██║   ██║██╔████╔██║{PURPLE}- DMIX({GREEN}dmix.co.za{GREEN}{ORANGE}){GREEN}
██╔══╝  ██║╚██╗██║██║   ██║██║╚██╔╝██║
███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║
╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝

           {RESET}""")

# declare a class
class DataRecord:
    def __init__(self, id, email, ip_address, username, password, hashed_password, name, vin, address, phone, database_name):
        self.id = id
        self.email = email
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hashed_password = hashed_password
        self.name = name
        self.vin = vin
        self.address = address
        self.phone = phone
        self.database_name = database_name

    def __repr__(self):
        return (f"DataRecord(id={self.id}, email={self.email}, ip_address={self.ip_address}, "
                f"username={self.username}, password={self.password}, hashed_password={self.hashed_password}, "
                f"name={self.name}, vin={self.vin}, address={self.address}, phone={self.phone}, "
                f"database_name={self.database_name})")

# declare Arguments class
class Arg:
    def __init__(self,api_key='',username='',domain='',email='',email_file='',output_file=''):
        self._api_key = api_key
        self._username = username
        self._domain = domain
        self._email = email
        self._email_file = email_file
        self._output_file = output_file

        @property
        def api_key(self):
            return str(self._api_key)
        @property
        def username(self):
            return str(self._username)
        @property
        def domain(self):
            return str(self._domain)
        @property
        def email(self):
            return str(self._email)
        @property
        def email_file(self):
            return str(self._email_file)
        @property
        def output_file(self):
            return str(self._output_file)

# argument management
def get_args():
    parser = argparse.ArgumentParser(description='Script description')
    parser.add_argument('-a', '--api_key',required=True, help='Dehashed api key')
    parser.add_argument('-u', '--username',required=True, help='Dehashed username subscription email')
    parser.add_argument('-d', '--domain',help='Target domain to query on dehashed.com')
    parser.add_argument('-e','--email',help='Email to query on dehashed.com')
    parser.add_argument('-f','--email_file', help='File containing email list')
    parser.add_argument('-o','--output_file',help='Directory to store your results, default=current directory')

    args = parser.parse_args()

    # criteria search argument
    search_criteria = ['email','email_file','domain']
    if not any(getattr(args,criteria) for criteria in search_criteria):
         parser.error(f'{RED}[-] At least one of {search_criteria} argument is required{RESET}')
    return Arg(**vars(args))


app_args = get_args()

# initialize base directory
base_directory =os.path.join( (app_args._output_file or os.getcwd()), 'dehashed')
dehashed_url = 'https://api.dehashed.com/search?query='
cracked_file_name = ''
hashed_file_name =''


# create directory if it does not exist
os.makedirs(base_directory,exist_ok=True)
if app_args._domain:
    os.makedirs(os.path.join(base_directory,app_args._domain),exist_ok=True)
    cracked_file_name = os.path.join(app_args._domain,'dehashed_cracked.txt')
    hashed_file_name = os.path.join(app_args._domain,'dehashed_hashed.txt')
elif app_args._email:
    os.makedirs(os.path.join(base_directory,app_args._email),exist_ok=True)
    cracked_file_name = os.path.join(app_args._email,'dehashed_cracked.txt')
    hashed_file_name = os.path.join(app_args._email,'dehashed_hashed.txt')
else:
    cracked_file_name = os.path.join('','dehashed_cracked.txt')
    hashed_file_name = os.path.join('','dehashed_hashed.txt')
cracked_file = os.path.join(base_directory,cracked_file_name)
hashed_file =os.path.join(base_directory,hashed_file_name)


def dehashed_domain_request():
     headers = {'Accept':'application/json'}
     response = requests.get(dehashed_url+f'domain:{app_args._domain}',headers=headers,auth=(str(app_args._username), str(app_args._api_key)))
     return response

def dehashed_email_request(email):
     headers = {'Accept':'application/json'}
     response = requests.get(dehashed_url+f'email:{email}',headers=headers,auth=(str(app_args._username), str(app_args._api_key)))
     return response

def get_query_response(response):
    # validate request
    if response.status_code !=200:
        sys.exit(f'{RED}[-] API Authentication Failed\n[-] Validate your api key and username{RESET}')
    return create_data_records(response)
def create_data_records(response) -> List[DataRecord]:
    # Parse the JSON response
    result_data = response.json()
    json_data = result_data['entries']

    # Ensure json_data is a list
    if not isinstance(json_data, list):
        json_data = [json_data]  # Wrap it in a list if it's a single dictionary

    # Create a list of DataRecord objects
    data = []
    for record in json_data:
        if record is not None:
            data.append(DataRecord(**record))

    return data or []

def dehashed_bulk_email_request(email_file):
    with open(email_file,'r') as file:
        emails = file.readlines()
        request_time = (5 + 0.5) *len(emails)
        minutes = request_time/60
        remaining_seconds = request_time%60

        print(f'{BLUE}[*] This will take {GREEN}{minutes:.0f}{BLUE} minutes and {GREEN}{remaining_seconds:.0f}{BLUE} seconds to complete{RESET}')
        for email in emails:
            response = dehashed_email_request(email)
            entries = get_query_response(response)
            results = get_result_lists(entries)
            save_to_file(results)
            sleep(0.5)

def get_result_lists(entries: List[DataRecord]):
    # Initialize sets to store unique pairs
    hashed_list = set()
    password_list = set()

    for entry in entries:
        # Ensure email is lowercase
        email = entry.email.lower()

        # Check for password
        if entry.password and len(entry.password) >= 1:
            password_list.add(f"{email} : {entry.password}")

        # Check for hashed_password (independent of password)
        if entry.hashed_password and len(entry.hashed_password) >= 1:
            hashed_list.add(f"{email} : {entry.hashed_password}")

    return password_list, hashed_list

def save_to_file(results):
    try:
        # Open files in append mode
        with open(cracked_file, 'a') as cracked, open(hashed_file, 'a') as hashed:
            # Save cracked passwords to file
            for result in results[0]:
                cracked.write(result + '\n')  # Add a newline for readability

            # Save hashed credentials to file
            for result in results[1]:
                hashed.write(result + '\n')  # Add a newline for readability
    except Exception as ex:
        print(f"An error occurred: {ex}")  # Print the exception for debugging

if __name__=="__main__":
    display_banner()

    # Handle requests
    if app_args._domain:
        print(f'{PURPLE}[!] Querying Dehashed for {GREEN}{app_args._domain}{RESET}')
        response = dehashed_domain_request()
        entries = get_query_response(response)
        results = get_result_lists(entries)
        save_to_file(results)
    elif app_args._email:
        print(f'{PURPLE}[!] Querying Dehashed for {GREEN}{app_args._email}{RESET}')
        response = dehashed_email_request(app_args._email)
        entries = get_query_response(response)
        results = get_result_lists(entries)
        save_to_file(results)
    elif app_args._email_file:
        print(f'{PURPLE}[!] Querying Dehashed for emails in {GREEN}{app_args._email_file}{RESET}')
        dehashed_bulk_email_request(app_args._email_file)
    print(f'{GREEN}[+] Done{RESET}')
    print(f'{GREEN}[+] Your results are saved in {ORANGE}{base_directory}{RESET}')
