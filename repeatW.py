#!/usr/bin/env python3

import os
import sys
import re
from bs4 import BeautifulSoup
import csv
import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from collections import defaultdict

file_path = os.path.realpath(__file__)
input_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "input.txt")
output30_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "output30.csv")
output40_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "output40.csv")
output50_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "output50.csv")
log_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "log.txt")

chrome_driver_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "chromedriver")
options = webdriver.ChromeOptions()
#options.add_argument("headless")
driver = webdriver.Chrome(executable_path= chrome_driver_path, options= options)

school_classes = ["I&C SCI", "MATH", "IN4MATX", "COMPSCI", "STATS"]
class_tracked = ["I&C SCI 31", "I&C SCI 32", "I&C SCI 32A", "I&C SCI 33", "I&C SCI 45C", "I&C SCI 45J", "I&C SCI 46", "I&C SCI 51", "I&C SCI 53"]
passing_grades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "P"]

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

def view_transcript():
        """
        Driver views Unofficial Transcript.
        """
        transcript = driver.find_element_by_link_text("Unofficial Transcript")
        transcript.click()

def download_page_source():
        """
        Downloads the current page driver is on.
        """
        return driver.page_source

"""Utility functions
"""
def parse_classes(page_source):
        """
        Given a page source of the unofficial transcript.
        Return classes that the user took in school of ICS.
        """
        soup = BeautifulSoup(page_source, features="html.parser")
        class_text = soup.body.find('table', attrs={'class': 'lineItems'}).text.split("\n")
        
        list_classes = []
        index = 0
        while index < len(class_text):
                if class_text[index] in school_classes and (class_text[index] + " " + class_text[index+1]) in class_tracked:
                        list_classes.append((class_text[index] + " " + class_text[index+1], class_text[index+3]))
                        index += 4
                else:
                        index += 1

        return sorted(list_classes)

def check_repeat(list_classes):
        """
        Given a list of classes the user took.
        Return classes that the user took twice and failed.
        """
        times_failed = defaultdict(int)

        for course, grade in list_classes:
                if grade not in passing_grades:
                        if course == "I&C SCI 32" or course == "I&C SCI 32A":
                                if times_failed["I&C SCI 32/32A"] != -1:
                                        times_failed["I&C SCI 32/32A"] += 1
                        else:
                                if times_failed[course] != -1:
                                        times_failed[course] += 1
                else:
                        if course == "I&C SCI 32" or course == "I&C SCI 32A":
                                times_failed["I&C SCI 32/32A"] = -1
                        else:
                                times_failed[course] = -1

        return [course for course in times_failed.items() if course[1] >= 2]

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

def main():
        """
        Main module
        """

        username, password = get_credentials()
        login(username, password)

        exists = os.path.isfile(input_file_path)
        if exists:
                file = open(input_file_path, "r")
                log = open(log_file_path, "w")
                
                csv30 = open(output30_file_path, "w", newline='', encoding='utf-8-sig')
                csv40 = open(output40_file_path, "w", newline='', encoding='utf-8-sig')
                csv50 = open(output50_file_path, "w", newline='', encoding='utf-8-sig')

                output30 = csv.writer(csv30)
                output40 = csv.writer(csv40)
                output50 = csv.writer(csv50)

                header = ["ID", "Name", "Email", "Class Failed (>= 2)"]
                output30.writerow(header)
                output40.writerow(header)
                output50.writerow(header)

                list_id = file.read().split("\n")
                for id_num in list_id:
                        enter_id(id_num.strip())
                        view_transcript()

                        transcript_download = download_page_source()
                        list_classes = parse_classes(transcript_download)
                        classes_repeated = check_repeat(list_classes)
                        name = find_name(transcript_download)
                        email = find_email(transcript_download)

                        passed = (classes_repeated == [])
                        log.write(name + "\n" + id_num + "\n" + email + "\n" + "Passed: " + "\t" + str(passed) + "\n\n")

                        list_class_names = [course[0] for course in classes_repeated]
                        if classes_repeated != []:
                                if "I&C SCI 31" in list_class_names or "I&C SCI 32/32A" in list_class_names or "I&C SCI 33" in list_class_names:
                                        output30.writerow([id_num, name, email, classes_repeated])
                                if "I&C SCI 45C" in list_class_names or "I&C SCI 45J" in list_class_names or "I&C SCI 46" in list_class_names:
                                        output40.writerow([id_num, name, email, classes_repeated])
                                if "I&C SCI 51" in list_class_names or "I&C SCI 53" in list_class_names:
                                        output50.writerow([id_num, name, email, classes_repeated])


                file.close()
                log.close()
                csv30.close()
                csv40.close()
                csv50.close()
        else:
                print("input.txt is missing.\n")

if __name__ == "__main__":
        main()
        driver.close()
        

