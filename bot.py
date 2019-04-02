import urllib.request
import os
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
file_path = os.path.abspath(__file__)
directory_path, filename = os.path.split(file_path)
chrome_driver_path = directory_path + "/chromedriver"
driver = webdriver.Chrome(executable_path= chrome_driver_path)

def enroll(lecture, dis):
	# driver.get('http://reg.uci.edu/')
	# input_text = driver.find_element_by_id("srchbox-input")
	# input_text.send_keys("Test")
	# input_text.submit()
	

	driver.get('https://www.reg.uci.edu/registrar/soc/webreg.html')
	login_button = driver.find_element_by_link_text("Access WebReg")
	login_button.click()
	time.sleep(5)


def check():
	list_codes = ["40261", "40262", "40263", "40264", "40265", "40266", "40267", "40268", "40269", "40270"]
	response = urllib.request.urlopen("https://www.reg.uci.edu/perl/WebSoc?YearTerm=2019-14&ShowFinals=1&ShowComments=1&Dept=CHEM&CourseNum=1C")
	page_source = response.read()
	soup = BeautifulSoup(page_source, features="html.parser")

	for script in soup(["script", "style"]):
		script.extract()

	text = soup.get_text()
	text = text.split("\n")

	dis_status = []
	lecture = "40260"

	index_start = text.index("CodeTypeSecUnitsInstructorTimePlaceFinalMaxEnrWLReqNorRstrTextbooksWebStatus")
	index_end = text.index("Class web site links (listed in \"Web\" column, /P indicates password required) provided by EEE.")
	for i in range(index_start, index_end):
		if text[i][0:5] in list_codes:
			dis_status.append((text[i][0:5], text[i].split()[len(text[i].split()) - 1]))

	for line in dis_status:
		if(line[1] == "OPEN"):
			enroll(lecture, line[1])
			exit(0)
		else:
			print("None OPEN")

if __name__ == "__main__":
	enroll("", "")


