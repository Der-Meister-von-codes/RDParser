#!/bin/python3

import os, requests, time
from datetime import datetime
from os.path import exists
from lxml import etree

os.system("clear")

print("""\
______ ______ ______
| ___ \|  _  \| ___ \\
| |_/ /| | | || |_/ /__ _  _ __  ___   ___  _ __
|    / | | | ||  __// _` || '__|/ __| / _ \| '__|
| |\ \ | |/ / | |  | (_| || |   \__ \|  __/| |
\_| \_||___/  \_|   \__,_||_|   |___/ \___||_|\n""")

search_url = "https://search.censys.io/_search?resource=hosts&sort=RANDOM&per_page=100&virtual_hosts=EXCLUDE&q=services.service_name%3A+rdp" #dork for censys to search machines with RDP ports
proxy_url  = "https://gimmeproxy.com/api/getProxy?curl=true&protocol=http&supportsHttps=true" 

print("Loading...")

#if tmp file exists, check if empty or older than 6 hours and overwrite or do nothing
if exists("tmp"):
	print("Tmp file is found!")
	t = open("tmp", "r")
	if len(t.read())==0 or (int(datetime.now().strftime("%s")) - 
int(time.strftime("%s", time.strptime(time.ctime(os.path.getmtime("tmp")))))) > 21600:
		print("File is old or void. Rewriting...")
		with open("tmp", "w+") as f:
			proxy_servers = {'http': requests.get(proxy_url).text} #add proxy for security
			f.write(requests.get(search_url, proxies=proxy_servers).text)
			print("Rewrited!")
		t.close()
#if not exists, just overwrite the file
else:
	print("Tmp file is not found. Creating...")
	with open("tmp", "w") as f:
		proxy_servers = {
			'http': requests.get(proxy_url).text
		}
		f.write(requests.get(search_url, proxies=proxy_servers).text)
		print("Success createrd and rewrited!")

print("Loading...")
with open("tmp", "r") as f:
	code = f.read() #read tmp as code for parsing
print("Loaded!")

print("Processing...")
dom = etree.HTML(code) #create etree object for parsing

data = [[0 for i in range(2)] for j in range(100)] #matrix array for convenient work with data

for i in range(99): #parse ip and port to matrix array 
	data[i][0] = dom.xpath(f'/html/body/div[{i+2}]/a/strong/text()')         #ip
	data[i][1] = dom.xpath(f'/html/body/div[{i+2}]/div/div[2]/div/a/text()') #ports

print("Data is processed!")

print("Writing to file...")
log = "" #create final output string in format valid for hydra
for i in range(99):
	for x in range(len(data[i][1])):
		if "/RDP" in data[i][1][x]: #if service in port is RDP add ip and port to final string
			log += str(data[i][0]).split("'")[1] + ":" + str(data[i][1][x]).split("/")[0] + "\n"

with open("targets", "w+") as f:
	f.write(log) #write final string to output file
	
print("Writed successfull!")
