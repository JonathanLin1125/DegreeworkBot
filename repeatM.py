#!/usr/bin/env python3

import os
import sys
from bs4 import BeautifulSoup
import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from collections import defaultdict

file_path = os.path.realpath(__file__)
input_file_path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/input.txt"
output_file_path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/output.txt"
log_file_path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/log.txt"

chrome_driver_path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/chromedriver"
options = webdriver.ChromeOptions()
#options.add_argument("headless")
driver = webdriver.Chrome(executable_path= chrome_driver_path, chrome_options= options)

school_classes = ["I&C SCI", "MATH", "IN4MATX", "COMPSCI", "STATS"]
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

	id_no = driver.find_element_by_name("_sid")
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
		if class_text[index] in school_classes:
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
				times_failed["I&C SCI 32/32A"] += 1
			else:
				times_failed[course] += 1

	return [course[0] for course in times_failed.items() if course[1] >= 2]

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
		output = open(output_file_path, "w")

		list_id = file.read().split("\n")
		for id_num in list_id:
			enter_id(id_num.strip())
			view_transcript()

			transcript_download = download_page_source()
			list_classes = parse_classes(transcript_download)
			classes_repeated = check_repeat(list_classes)

			passed = (class_repeated == [])
			log.write(id_num + "\n" + "Passed: " + "\t" + str(passed) + "\n\n")

			if class_repeated != []:
				output.write(id_num + "\n\n")

		file.close()
		log.close()
		output.close()
	else:
		print("input.txt is missing.\n")

if __name__ == "__main__":
	main()
	
	# transcript_download = download_page_source()
	# list_classes = parse_classes(transcript_download)
	# classes_repeated = check_repeat(list_classes)



	# print("ICS classes taken")
	# for c in list_classes:
	# 	print(c)

	# if classes_repeated == []:
	# 	print("\nNo classes repeated two or more times\n")
	# else:
	# 	print(classes_repeated)
