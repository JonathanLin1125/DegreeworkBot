#!/usr/bin/env python3

import urllib.request
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
output_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "output.txt")
log_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "log.txt")
chrome_driver_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "chromedriver")

options = webdriver.ChromeOptions()
#options.add_argument("headless")
driver = webdriver.Chrome(executable_path= chrome_driver_path, options= options)

gpa_scale = {"A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0}
school_classes = ["I&C SCI", "MATH", "IN4MATX", "COMPSCI", "STATS"]
ics_majors = ["Business Information Management", "Computer Science", "Computer Game Science", "Computer Science and Engineering", "Data Science", "Software Engineering", "Informatics"]
ics_minors = ["Bioinformatics", "Digital Information Systems", "Health Informatics", "Informatics", "Information and Computer Science", "Statistics"]
pnp_classes = ["I&CSCI 90"]

"""Driver functions
"""
def login(username, password):
	"""
	Driver logs into WebAdmin.
	"""
	driver.get('https://www.reg.uci.edu')
	studentAccess = driver.find_element_by_link_text("StudentAccess")
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
	Returns a list of courses student took to complete major.
	"""
	soup = BeautifulSoup(page_source, features="html.parser")
	sections = soup.body.find_all('table', attrs={'border': "0"})

	if major in ics_majors:
		for section in sections:
			try:
				major_found = section.find('td', attrs={'class': "BlockHeadTitle"}).text.strip()[9:]
				if major_found in ics_majors and major_found == major:
					course_sections = section.find_all('tr', attrs={'class': re.compile(r'bgLight(100|98|0)')})
					for course_section in course_sections:
						try:
							courses = course_section.find_all('tr', attrs={'class': 'CourseAppliedRowWhite'})
							for course in courses:
								course_title = course.find('td', attrs={'class': "CourseAppliedDataDiscNum"}).text.strip()
								course_grade = course.find('td', attrs={'class': 'CourseAppliedDataGrade'}).text.strip()
								if "(T)" not in course_title and course_grade != "T" and course_grade != "IP":
									list_courses.add((course_title, course_grade))
						except:
							pass
					break
			except:
				pass
	return list_courses

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

	view_degree_works()
	page_source = download_degree_source()

if __name__ == "__main__":
	retrieve_information()

