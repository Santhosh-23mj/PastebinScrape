#!/usr/bin/python3

import os
import time
import argparse
import urllib.request
import concurrent.futures
from bs4 import BeautifulSoup

linkDic = {}

def getHTML(url):
	webPage = urllib.request.urlopen(url)
	return webPage.read()


def getLinks(webPage):
	soup = BeautifulSoup(webPage, 'html.parser')
	tableData = soup.find_all('td')
	for td in tableData:
		link = td.find('a')
		if(link and not link.text == 'None'):
			uri = "https://pastebin.com" + str(link.get('href'))
			linkDic[link.text] = uri

 
def getPageNo(url):
	webPage = getHTML(url)
	soup    = BeautifulSoup(webPage, 'html.parser')
	pageNo  = len(soup.find('div',attrs = {'class':'pagination'}).findAll('a'))
	return webPage, pageNo


def writeLinks():
	print("---------------------------------------------------------")
	with open('links.txt',"w") as f:
		for name, link in linkDic.items():
			print("{:<25} {}".format(name, link))
			f.write("{:<25} {}\n".format(name, link))
	print("---------------------------------------------------------")


def createFile(filename, data):
	with open(filename,"w") as f:
		f.write(data)


def getData(nameLinkTuple):
	webPage = getHTML(nameLinkTuple[1])
	soup    = BeautifulSoup(webPage, 'html.parser')
	data    = soup.find('textarea').text
	# Comment this if you donot want to fill the screen.
	print("[+] Getting data from {} - {}".format(nameLinkTuple[0], nameLinkTuple[1]))
	createFile(nameLinkTuple[0], data)


def main():
	print("[!] Starting at : " + str(time.asctime()))
	print("=========================================================")
	startTime = time.time()
	parser = argparse.ArgumentParser()
	parser.add_argument("-u","--username", help = "Specify the username of the pastebin account", required = True)
	parser.add_argument("-d","--data", help = "If you want to download the pastes", action = 'store_true')
	parser.add_argument("-t","--threads", help = "No. of threads to run", type = int, default = 10)
	args = parser.parse_args()
	
	url = "https://pastebin.com/u/" + args.username + "/1"
	
	webPage, pageNo = getPageNo(url)
	
	print("[*] The user has {} pages".format(pageNo-1))
	print("[+] Getting Links from Page : 1")
	getLinks(webPage)
	
	if(pageNo > 2):
		for i in range(2,pageNo):
			print("[+] Getting Links from Page : " + str(i))
			url     = "https://pastebin.com/u/" + args.username + "/" + str(i)
			webPage = getHTML(url)
			getLinks(webPage)
	writeLinks()
	print("[+] Wrote all links to links.txt")
	
	if(args.data):
		if(not os.path.isdir(args.username)):
			os.mkdir(args.username)
		os.chdir(args.username)
		print("[+] Getting data from all Pastes !")
		with concurrent.futures.ThreadPoolExecutor(max_workers = args.threads) as Executor:
			Executor.map(getData, list(linkDic.items()))
	print("[+] Done !")
	print("=========================================================")
	print("[!] Finished at      : " + str(time.asctime()))
	print("[+] Time to complete : {}s".format(str(time.time() - startTime)[:-12]))
	
if(__name__ == "__main__"):
	main()
