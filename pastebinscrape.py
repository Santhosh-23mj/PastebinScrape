#!/usr/bin/env python3

"""
A Program to scrape Pastebin, without use of any API.
    1. Get most recent public pastes
    2. Get usernames from the most recent public pastes
    3. Get data from all public pastes
    4. Get all public pastes from a specific username
    5. Get data from all public pastes of a user

#TODO
Implement Search based on Syntax, which fetches most recent public
pastes based on the syntax.
"""
import os
import csv
import time
import argparse
import urllib.request
from bs4 import BeautifulSoup
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor
 
HEADERS = ["Title", "URL", "Syntax"]
ALLLIST = []
    
def getLinks(url):
    """
    A function to get all the hyperlinks to pastes from <a> tags in the given url.
    """
    linkList = []
    synList  = []
    try:
        webPage   = urllib.request.urlopen(url).read()
    except Exception as e:
        print("[EXCEPTION] ",e)
        print("[!] Check Internet Connection.")
        exit(0)
    soup      = BeautifulSoup(webPage, 'html.parser')
    tableData = soup.find_all('td')
    for td in tableData:
        link = td.find('a')
        if(link and 'archive' not in link.get('href')):
            linkList.append(link)
        if(link and 'archive' in link.get('href')):
            synList.append(link)
    linkSyn = zip(linkList, synList)
    for element in linkSyn:
        temp = []
        temp.append(element[0].text)
        # Appending /raw so it makes getting data from pastes easier.
        temp.append("https://pastebin.com/raw" + element[0].get('href'))
        temp.append(element[1].text)
        ALLLIST.append(temp)
        
def getPageNo(url):
    """
    A function to get the number of pages a user has in his pastebin
    """
    try:
        webPage = urllib.request.urlopen(url).read()
    except Exception as e:
        print("[EXCEPTION] ",e)
        print("[!] Check Internet Connection.")
        exit(0)
    soup    = BeautifulSoup(webPage, 'html.parser')
    pageNo  = len(soup.find('div',attrs = {'class':'pagination'}).findAll('a'))
    return pageNo

def createFile(filename, data):
    """
    A function to create files for given data. Just to minimize redundancy.
    """
    # A csv file to put all links and titles
    with open(filename, "w") as fileobj:
        if('csv' in filename):
            csvWriter = csv.writer(fileobj)
            csvWriter.writerow(HEADERS)
            for row in data:
                csvWriter.writerow(row)
        else:
            fileobj.write(data)
    
def checkDir(directory):
    """
    A function to check if the directory is present, if not create one. Then move
    to the directory. Just to eliminate redundancy.
    """
    if(not os.path.isdir(directory)):
        os.mkdir(directory)
    os.chdir(directory)
    
def getData(nameLink):
    """
    A function to get the data from the given pastebin URL and create a File
    based on the Title in nameLink.
    """
    try:
        webPage = urllib.request.urlopen(nameLink[1]).read()
    except Exception as e:
        print("[EXCEPTION] ",e)
        print("[!] Check Internet Connection.")
        exit(0)
    data    = webPage.decode()
    createFile(nameLink[0], data)
    
def getUsernames(nameLink):
    """
    A function to get the Usernames from the most recent Public Pastes.
    """
    url = nameLink[1].replace("raw/","")
    try:
        webPage  = urllib.request.urlopen(url).read()
    except Exception as e:
        print("[EXCEPTION] ",e)
        print("[!] Check Internet Connection.")
        exit(0)
    soup = BeautifulSoup(webPage,'html.parser')
    nameLink.append(soup.find('div',attrs = {'class':'username'}).text.strip())

def userThread(threads):
    """
    A function to run the Threading for getUsername() function.
    """
    with ThreadPoolExecutor(max_workers = threads) as executor:
        executor.map(getUsernames, ALLLIST)

def dataThread(threads):
    """
    A function to run the threading for getData() function
    """
    with ThreadPoolExecutor(max_workers = threads) as executor:
        executor.map(getData, ALLLIST)

def main():
    """
    Main function to do all the necessary functions.
    """
    
    start  = time.time()
    parser = argparse.ArgumentParser(description = "A Pastebin scraper without the use of API")
    group  = parser.add_mutually_exclusive_group(required = True)
    group.add_argument("-u", "--username", help = "Specify the username to scrape contents from")
    group.add_argument("-p","--public", help = "If you want to fetch most recent Public Pastes", action = 'store_true')
    parser.add_argument("-d","--data", help = "If you want to get data from all the pastes", action = 'store_true')
    parser.add_argument("-t","--threads", help = "No of threads to run", type = int, default = 10)
    parser.add_argument("--get-usernames", help = "if you want usernames from public pastes", action = 'store_true')
    args = parser.parse_args()
    
    if(args.get_usernames and args.username):
        print("[-] Cannot use --get-username with -u. Please view help (-h)")
        exit(0)
	
    print("[!] Starting at : " + str(time.asctime()))
    print("=========================================================")
		
    if(args.username):
        url = "https://pastebin.com/u/" + args.username
        print("[+] Getting Pages for {} ".format(args.username))
        pageNo = getPageNo(url)
		
        if(pageNo == 0):
            print("[+] {} has only one page".format(args.username))
            print("[+] Getting Links !")
            getLinks(url)
        else:
            print("[+] {} has {} pages".format(args.username, pageNo))
            print("[+] Getting Links !")
            for i in range(1,pageNo):
                url = "https://pastebin.com/u/" + args.username + "/" + str(i)
                getLinks(url)

        print("[+] Fetched the Links!")
        print(tabulate(ALLLIST, headers = HEADERS, tablefmt = "rst"))
        createFile(args.username + ".csv", ALLLIST)
		
        if(args.data):
            print("[+] Getting data from all pastes of {}".format(args.username))
            checkDir(args.username)
            print("[+] Running {} threads".format(args.threads))
            dataThread(args.threads)
            print("[+] Got all data written to {} directory".format(args.username))
	
    if(args.public):
        print("[+] Getting most recent Public pastes!")
        url = "https://pastebin.com/archive"
        getLinks(url)
        print("[+] Fetched all Links!")

        if(args.get_usernames):
            print("[+] Getting Usernames for all those pastes!")
            HEADERS.append("Username")
            print("[+] Running {} threads".format(args.threads))
            userThread(args.threads)
            print("[+] Got all usernames.")

        print(tabulate(ALLLIST, headers = HEADERS, tablefmt = "rst"))
        createFile("PublicPastes.csv", ALLLIST)
		
        if(args.data):
            print("[+] Getting data from all recent public pastes.")
            checkDir("PublicPastes")
            print("[+] Running {} threads".format(args.threads))
            dataThread(args.threads)
            print("[+] Got all data written to PublicPastes directory")
		
    print("[+] Done with Everything, Quitting!")
    print("=========================================================")
    print("[!] Finished at      : " + str(time.asctime()))
    print("[+] Time to complete : {}s".format(str(time.time() - start)[:-12]))

if(__name__ == "__main__"):
	main()
