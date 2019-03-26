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
chrome_driver_path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/chromedriver"
options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(executable_path= chrome_driver_path, chrome_options= options)

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
	driver.switch_to_default_content()
	driver.switch_to.frame("frHeader")
	access = driver.find_element_by_link_text("Back to StudentAccess")
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
	driver.switch_to_default_content()
	driver.switch_to.frame("frBodyContainer")
	driver.switch_to.frame("frBody")
	return driver.page_source

"""Utility functions
"""
def find_units(page_source):
	"""
	Given a page source of degreeworks.
	Returns the number of units applied to degreeworks.
	"""
	soup = BeautifulSoup(page_source, features="html.parser")
	unit_text = soup.body.find_all('td', attrs={'class': 'BlockHeadSubData', 'align': 'left'})

	return float(unit_text[1].text.strip())

def find_overall_gpa(page_source):
	"""
	Given a page source of degreeworks.
	Returns the overall gpa.
	"""
	soup = BeautifulSoup(page_source, features="html.parser")
	gpa_text = soup.body.find_all('tr', attrs={'class': 'StuTableTitle'})

	for entry in gpa_text:
		try:
			if entry.find("td", attrs={'class': 'StuTableTitle'}).text.strip() == "Overall GPA":
				return(float(entry.find("td", attrs={'class': 'StuTableData'}).text.strip()))
		except:
			pass #It'll be okay :)
	return 0.0

def find_major_courses(page_source, major):
	"""
	Given a page source of degreeworks
	Returns a list of courses student took to complete major.
	"""
	soup = BeautifulSoup(page_source, features="html.parser")
	sections = soup.body.find_all('table', attrs={'border': "0"})

	list_courses = set()
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

def find_minor_courses(page_source, minor):
	"""
	Given a page source of degreeworks
	Returns a list of courses student took to complete major.
	"""
	soup = BeautifulSoup(page_source, features="html.parser")
	sections = soup.body.find_all('table', attrs={'border': "0"})

	list_courses = set()
	if minor in ics_minors:
		for section in sections:
			try:
				minor_found = section.find('td', attrs={'class': "BlockHeadTitle"}).text.strip()[9:]
				if minor_found in ics_minors and minor_found == minor:
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

def find_major_minor(page_source):
	"""
	Given a page source of degreeworks.
	Returns the major(s) & minor(s).
	"""
	soup = BeautifulSoup(page_source, features="html.parser")
	sections = soup.body.find_all('tr', attrs={'class': re.compile(r'StuTableTitle')})

	list_majors = []
	list_minors = []
	for section in sections:
		row = section.text.strip().split("\n")
		if row[0] == "Grad App Status":
			start_index = row.index("Major")
			for index in range(start_index + 1, len(row)):
				list_majors.append(row[index])
		if row[0] == "Overall GPA":
			start_index = row.index("Minor")
			for index in range(start_index + 1, len(row)):
				list_minors.append(row[index])
	return list_majors, list_minors

def find_upper_gpa(page_source):
	"""
	Given a page source of the unofficial transcript.
	Return gpa of upper-div classes that the user took in school of ICS.
	"""
	soup = BeautifulSoup(page_source, features="html.parser")
	class_text = soup.body.find('table', attrs={'class': 'lineItems'}).text.split("\n")

	earned_gpa = 0.0
	total_gpa = 0.0
	index = 0
	while index < len(class_text):
		if class_text[index] in school_classes and re.search("1[0-9][0-9]", class_text[index+1]) and class_text[index+3] in gpa_scale:
			earned_gpa += float(class_text[index+4])
			total_gpa += 4.0 * float(class_text[index+2])
			index += 5
		else:
			index += 1

	return (earned_gpa/total_gpa) * 4.0

def find_all_major_minor(page_source, majors, minors):
	"""
	Given page source of degreeworks.
	Returns dict of each major/minor with corresponding courses taken.
	"""
	major_classes = dict()
	minor_classes = dict()
	for major in majors:
		if major in ics_majors:
			major_classes[major] = find_major_courses(page_source, major)
	for minor in minors:
		minor_classes[minor] = find_minor_courses(page_source, minor)
	return major_classes, minor_classes

def is_all_letter_grade(major_classes):
	"""
	Given a dict of majors and coressponding classes.
	Return true if all classes are taken for grade, false otherwise.
	"""
	for major in major_classes.items():
		for course in major[1]:
			if course[0] not in pnp_classes and course[1] == "P":
				return False 
	return True
	
def is_overlapping_major_minor(major_classes, minor_classes):
	"""
	Given a list of classes for a major and minor.
	Return true if less than 5 overlapping, false otherwise.  
	"""
	for major in major_classes:
		for minor in minor_classes:
			unique_class = 0
			for course in minor_classes[minor]:
				if course not in major_classes[major]:
					unique_class += 1
			if unique_class < 5:
				return False 
	return True

def is_complete(page_source):
	"""
	Given a page source of degreeworks.
	Returns a list of incomplete sections.
	"""
	soup = BeautifulSoup(page_source, features="html.parser")
	all_sections = soup.body.find_all('tr', attrs={'class': 'bgLight0'})
	return len(all_sections) == 0

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
	view_transcript()
	transcript_source = download_transcript_source()
	u_gpa = find_upper_gpa(transcript_source)

	view_degree_works()
	degree_source = download_degree_source()

	majors, minors = find_major_minor(degree_source)
	units = find_units(degree_source)
	o_gpa = find_overall_gpa(degree_source)
	completed = is_complete(degree_source)
	major_classes, minor_classes = find_all_major_minor(degree_source, majors, minors)
	letter_grade = is_all_letter_grade(major_classes)
	overlap = is_overlapping_major_minor(major_classes, minor_classes)

	print("\nTotal Units: ", units)
	print("Overall GPA: ", o_gpa)
	print("Upper Div GPA: ", u_gpa)
	print("Completed all courses? ", completed)
	print("Major(s): ", majors)
	print("Minor(s): ", minors)
	print("All major classes taken with letter grade? ", letter_grade)
	print("All minors do not have 5 or more overlapping with major? ", overlap)
	print("")

	go_back_to_access()

if __name__ == "__main__":
	username, password = get_credentials()
	login(username, password)

	retrieve_information()

