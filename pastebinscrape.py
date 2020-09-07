#!/usr/bin/python3

import os
import argparse
import threading
import mechanize
from bs4 import BeautifulSoup

linkDic = {}

def getPage(url):
	"""Function to get the HTML document from the specified URL"""
	browser = mechanize.Browser()
	browser.set_handle_robots(False)
	webPage = browser.open(url)
	return webPage


def getNoofPages(webPage):
	"""Function to get the number of pages the users has pastes"""
	soup = BeautifulSoup(webPage, 'html.parser')
	pages = len(soup.find("div", attrs = {'class' : 'pagination'}).findAll('a'))
	return pages


def getLinks(webPage):
	"""Function to parse the webpage and fetch links"""
	soup = BeautifulSoup(webPage, 'html.parser')
	
	# Fetch all table data <td> tags
	tableData = soup.find_all('td')
	
	# Get all <a> tags from <td> with links
	for td in tableData:
		link = td.find('a')
		if(link and not link.text == 'None'):
			uri = "https://www.pastebin.com"+str(link.get('href'))
			linkDic[link.text] = uri


def printLinks():
	"""Function to print the values in the Dictionary"""
	with open("links.txt",'w') as f:
		for name, link in linkDic.items():
			print("{:<25}  {:<25}".format(name,link))
			f.write("{:<25}  {}\n".format(name,link))


def createFile(filename, data):
	"""Function to create a file for each data from each link"""
	with open(filename,"w") as f:
		f.write(data)


def getData(username):
	"""Function to fetch the data from each links"""
	for name, link in linkDic.items():
		webPage  = getPage(link)
		soup     = BeautifulSoup(webPage, 'html.parser')
		data     = soup.find('textarea').text
		filename = os.path.join(username,name)
		print("[+] Getting data from {} and writing to {} !".format(link, filename))
		createFile(filename, data)


def main():
	"""Main function"""
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-u","--username", help = "specify the pastebin username", required = True)
	parser.add_argument("-d","--data", help = "To get the data from all the links", action = 'store_true')
	args = parser.parse_args()
	
	url = "https://pastebin.com/u/" + args.username + "/1"
	
	# Fetching the HTML document
	webPage = getPage(url)
	
	# Parsing the document to find the number of pages
	pageNo = getNoofPages(webPage)
	
	# Parsing the pages to get the links
	for i in range(1,pageNo):
		url = "https://pastebin.com/u/" + args.username + "/" + str(i)
		webPage = getPage(url)
		getLinks(webPage)
	printLinks()
	
	
	if(args.data):
		if(not os.path.isdir(args.username)):
			os.mkdir(args.username)
		print()
		print("[+] Getting data from all pastes !")
		getData(args.username)
		print("[+] Done !")
		print()
	

if(__name__ == "__main__"):
	main()
