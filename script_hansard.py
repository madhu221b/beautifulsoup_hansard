'''
This script downloads all the .txt files from Hansard portal.
Usage: python script_hansard.py 100 200
Say, you have to download all txts of all the rows belonging from page 100
to page 200.
'''

import os
import sys
import time
from datetime import datetime
from dateutil import parser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

start_index, end_index = -1, -1

HOME_DIRECTORY = "/home/madhu221b"
DRIVER_PATH = HOME_DIRECTORY + "/Downloads/chromedriver_linux64/chromedriver"
CURRENT_DIRECTORY =  HOME_DIRECTORY + "/Documents/dataset_hansard"
PARENT_LINK = "https://hansard.parliament.uk/"
URL = "https://hansard.parliament.uk/search/Contributions?endDate=1951-01-26&searchTerm=india&startDate=1800-01-01&page="
TRACE_PATH = "trace.txt"


if not os.path.exists(CURRENT_DIRECTORY):
    os.mkdir(CURRENT_DIRECTORY)

try:
    if len(sys.argv) == 3:
       start_index, end_index = int(sys.argv[1]), int(sys.argv[2])
    else:
       print("Enter a starting index and ending index for the documents you wish to download.")
except ValueError:
    print("Enter integer indices.")
    pass
except Exception:
    print("Make sure indices are valid")

prefs = {
    "download.default_directory": CURRENT_DIRECTORY,
    "download.prompt_for_download": False
}

service = Service(DRIVER_PATH)
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(service=service, options=options)

def return_soup(url:str, sleep_time:int):
    """Function for computing the html of the page given the url.

        Args:
           url: URL of the page to parse.
           sleep_time: Since Javascript takes time to load, the time
                       we want to wait for page to load with results.

        Returns:
              The html parsed data
    """
    try:
        driver.get(url)
        time.sleep(sleep_time)
       #  WebDriverWait(driver, sleep_time).until(EC.presence_of_element_located((By.CLASS_NAME, 'card card-calendar')))
        soup = BeautifulSoup(driver.page_source)
        return soup
    except TimeoutException:
        print("Page is taking time to load.")
        return None
    except Exception as error:
        print("return_soup error: ", error)
        return None    

def download_txt(url: str)-> bool:
    """Function to click on hyperlink to download txt

        Args:
           url: URL of the page to download.

        Returns:
              Boolean based on whether the txt is downloaded successfully.
    """
    try:
      driver.get(url)
      driver.implicitly_wait(2)
      main_button = driver.find_element(by=By.CLASS_NAME, value='icon-link')
      main_button.click()
      driver.implicitly_wait(2)
    except Exception as error:
        print("download_txt error: ", error)
        return False

def count_files(directory:str)-> int:
    try:
        return len([name for name in os.listdir(directory) \
         if os.path.isfile(os.path.join(directory, name))])
    except Exception as error:
        print("count files error: ", count_files)
        return -1

def get_failed_documents(global_list: list):
    try:
        dir_list = [] 
        for filename in os.listdir(CURRENT_DIRECTORY):
            arr = filename.split()
            element = None
            if ").txt" in arr[-1]:
               element = " ".join(arr[:-1])
            else:
                last_item = arr[-1].split(".")[0]
                arr[-1] = last_item
                element = " ".join(arr)
            if element: dir_list.append(element)
        # print("global list: ", set(global_list))
        # print("dir list: ", set(dir_list))
        
        no_list = set(global_list) - set(dir_list)
        print(list(no_list), file=open("failed_docs.txt", "a"))
    except Exception as error:
        print("get_failed_documents: ", error)
try:
    if start_index != -1 and end_index != -1 and end_index >= start_index:
        curr_index = start_index
        is_continue = True
        global_list = []
        while True:
            url_rows_page = URL + str(curr_index)
            soup_rows = return_soup(url_rows_page, 3)
            links_pages = []
            print("url row page: ", url_rows_page)
            if soup_rows:
                array_rows = soup_rows.findAll("a", {"class": "card card-calendar"})
                for item in array_rows:
                    links_pages.append(PARENT_LINK + item["href"])
                    title = item.find("div", {"class": "primary-info"}).text.strip()
                    date = item.find("div", {"class": "tertiary-info"}).text.strip()
                    file_name = title + " " + str(parser.parse(date, yearfirst=True)).split()[0]
                    global_list.append(file_name)
                    print("filename: ", file_name)
            else:
                links_pages = []
            print("Rows on the page: ", len(links_pages))
            
            for link in links_pages:
                    is_downloaded = download_txt(link)
                    
                    if is_downloaded:
                        print("Page: {}, File : {} downloaded/not exists. End time : {}".format(curr_index, link, datetime.now()), \
                        file=open(TRACE_PATH, "a"))
                    else:
                        print("Page: {}, File : {} download FAILED. End time : {}".format(curr_index, link, datetime.now()), \
                        file=open(TRACE_PATH, "a"))
            
            curr_index += 1
            if curr_index > end_index:
                break

        time.sleep(5)
        get_failed_documents(global_list)
except Exception as error:
    print("Error while execution of script:", error)
        



