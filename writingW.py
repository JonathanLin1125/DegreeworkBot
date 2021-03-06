#!/usr/bin/env python3

import urllib.request
import csv
import os
import sys
from bs4 import BeautifulSoup
import time
import getpass
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from collections import defaultdict

file_path = os.path.realpath(__file__)
input_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "input.txt")
output_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "output.csv")
log_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "log.txt")
chrome_driver_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "chromedriver")

options = webdriver.ChromeOptions()
#options.add_argument("headless")
driver = webdriver.Chrome(executable_path= chrome_driver_path, options= options)

"""Driver functions
"""
def login(username, password):
        """
        Driver logs into WebAdmin.
        """
        driver.get('https://www.reg.uci.edu')
        studentAccess = driver.find_element_by_link_text("WebAdmin")
        studentAccess.click()

        login = driver.find_element_by_link_text("Click here to Login.")
        login.click()
        
        user_name = driver.find_element_by_id("ucinetid")
        user_name.send_keys(username)
        pass_word = driver.find_element_by_id("password")
        pass_word.send_keys(password, Keys.ENTER)

def enter_id(id_num):
        """
        Driver enters an id for WebAdmin
        """
        welcome = driver.find_element_by_link_text("Welcome")
        welcome.click()

        id_no = driver.find_element_by_name("sid")
        id_no.send_keys(id_num, Keys.ENTER)

def view_degree_works():
        """
        Driver views Degree Works.
        """
        degree = driver.find_element_by_link_text("DegreeWorks")
        degree.click()

def go_back_to_access():
        """
        Driver goes back to studentaccess from degreeworks.
        """
        driver.switch_to.default_content()
        driver.switch_to.frame("frHeader")
        access = driver.find_element_by_link_text("Back to WebAdmin")
        access.click()

def view_transcript():
        """
        Driver views Unofficial Transcript.
        """
        transcript = driver.find_element_by_link_text("Unofficial Transcript")
        transcript.click()

def download_transcript_source():
        """
        Downloads the current page driver is on. (Transcripts)
        """
        return driver.page_source

def download_degree_source():
        """
        Downloads the current page driver is on. (degreeworks)
        NOTE: Framesets are automatically expanded, to expand a frame, you must switch into it.
        """
        driver.switch_to.default_content()
        driver.switch_to.frame("frBodyContainer")
        driver.switch_to.frame("frBody")
        return driver.page_source

"""Utility functions
"""
def lower_writing_complete(page_source):
        """
        Given a page source of degreeworks
        Returns whether student finished their lower division writing requirements.
        """
        soup = BeautifulSoup(page_source, features="html.parser")
        sections = soup.body.find_all('table', attrs={'border': "0"})

        for section in sections:
                block_name = section.find('td', attrs={'class': "BlockHeadTitle"})
                if block_name != None and block_name.text.strip() == "General Education Requirements":
                        ge_sections = section.find_all('tr', attrs={'class': 'bgLight0'})
                        for ge in ge_sections:
                                title = ge.find('td', attrs={'class': 'RuleLabelTitleNeeded'})  
                                if title != None and (title.text.strip() == "I. Lower-Division Writing (minimum grade C)"):
                                        return False    
        return True

def find_name(page_source):
        """
        Given a page souce of unofficial transcript
        Returns the student's name.
        """
        soup = BeautifulSoup(page_source, features="html.parser")
        name = soup.body.find('span', attrs={'onmouseout': 'kill();'})
        if name != None:
                return name.text.strip()
        else:
                return "NULL"

       
def find_email(page_source):
        """
        Given a page source of unofficial transcript
        Returns the student's email.
        """
        soup = BeautifulSoup(page_source, features='html.parser')
        email_locations = soup.body.find_all('td')

        for email in email_locations:
                if re.match("^[A-Za-z0-9]*@uci\.edu$", email.text.strip()):
                        return email.text.strip()
        return "NULL"


def get_credentials():
        """
        Prompts user for login crednetials
        """
        username = getpass.getpass("Enter UCInetID: ")
        password = getpass.getpass("Enter password: ")
        return username.strip(), password.strip()


def retrieve_information():
        """
        Retrieves all information given a driver that is on a student's studentaccess.
        """
        username, password = get_credentials()
        login(username, password)

        exists = os.path.isfile(input_file_path)
        if exists:
                file = open(input_file_path, "r")
                log = open(log_file_path, "w")
                with open(output_file_path, "w", newline='', encoding = 'utf-8-sig') as csvfile:
                        output = csv.writer(csvfile)
                        output.writerow(["ID", "Name", "Email"])

                        list_id = file.read().split("\n")
                        for id_num in list_id:
                                enter_id(id_num.strip())

                                page_source = download_transcript_source()
                                name = find_name(page_source)
                                email = find_email(page_source)
                                
                                view_degree_works()
                                page_source = download_degree_source()
                                go_back_to_access()

                                lwd_complete = lower_writing_complete(page_source)

                                log.write(name + "\n" + id_num + "\n" + email + "\n" + str(lwd_complete) + "\n\n")
                                if not lwd_complete:
                                        output.writerow([id_num, str(name), email])

                file.close()
                log.close()

if __name__ == "__main__":
        retrieve_information()
        driver.close()

