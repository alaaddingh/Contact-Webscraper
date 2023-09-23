import requests
from bs4 import BeautifulSoup
import re  # regex
import time
import pandas as pd
from random import randint  # used for choosing a random header
import os
from googlesearch import search
start_time = time.time()

# allows us a list of headers to send.
# check headers with: http://httpbin.org/headers
SCRAPEOPS_API_KEY = '59cfb68f-5843-432f-a4d3-81e93fa9a30e'


def get_headers_list():
    response = requests.get(
        'http://headers.scrapeops.io/v1/browser-headers?api_key=' +
        SCRAPEOPS_API_KEY)
    json_response = response.json()
    return json_response.get('result', [])


def get_random_header(header_list):
    random_index = randint(0, len(header_list) - 1)
    return header_list[random_index]


def get_all_websites():
    print("Welcome to the Contact Webscraper!")
    searched = input("\nPlease Enter a Google search:\n")
    search_results = list(search(searched, 10, 10))

    # Extract actual URLs from search results
    web_list = [result for result in search_results if result.startswith("http")]

    return web_list


def get_email_and_numbers(m, the_header):
    try:
        # requests (from web_list) website's html

        request = requests.get(m, headers=the_header)
        request.raise_for_status()  # Check for any errors in the response

        # Parses HTML with BeautifulSoup
        soup = BeautifulSoup(request.content, 'html.parser')
        emails = []
        phone_numbers = []
        email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b')
        phone_pattern = re.compile(
            r'\b(?:(?:\+\d{1,2}[-.\s]*)?(?:(?:\(\d{3}\)|[2-9]\d{2})(?:[-.]|\s?-\s?|\s?\.\s?)\d{3}(?:[-.]|\s?-\s?|\s?\.\s?)\d{4}))\b')
        for word in soup.find_all():
            word_text = word.get_text()
            email_matches = email_pattern.findall(word_text)
            phone_matches = phone_pattern.findall(word_text)
            emails.extend(email_matches)
            phone_numbers.extend(phone_matches)

        if emails:
            emails = set(emails)
            emails = list(emails)
        emails.insert(0, "EMAILS:")
        if phone_numbers:
            phone_numbers = set(phone_numbers)
            phone_numbers = list(phone_numbers)
        phone_numbers.insert(0, "PHONE NUMBERS:")
        emails_and_nums = emails + phone_numbers
        return emails_and_nums

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while processing {m}: {str(e)}")
        return []


def table_concat(found_emails, m):
    # combine different data (from one website) into ONE COLUMN
    column = found_emails_and_nums
    column_dataframe = pd.DataFrame({m: column})  # "DataFrame form"
    return column_dataframe


# ------------------------------------------
# MAIN PROGRAM
if __name__ == "__main__":
    header_list = get_headers_list()
    the_header = get_random_header(header_list)
    web_list = get_all_websites()
    # next two lines set's up the table
    d = []
    table = pd.DataFrame(d)
    for m in web_list:  # iterates through each website (m) on the list and performs necessary tasks
        found_emails_and_nums = get_email_and_numbers(m, the_header)  # PRIMARY VARIABLE
        column_dataframe = table_concat(found_emails_and_nums, m)
        # concatenate current column to previous (side by side)
        table = pd.concat([table, column_dataframe], axis="columns")

    print("\n-------final table---------")
    print(table)
    user_home = os.path.expanduser("~")

    # Define the filename and folder in the documents directory
    filename = input("Enter a name for your file:\n")
    file_name = filename + ".csv"
    documents_folder = "Documents"

    # Construct the full path to the CSV file
    csv_path = os.path.join(user_home, documents_folder, file_name)

    # Use pandas to save the DataFrame to the CSV file
    table.to_csv(csv_path, index=False, header=True)
    print("\nDone!")
    print("Process finished --- %s seconds ---" % (time.time() - start_time) + "\n\n\n")


