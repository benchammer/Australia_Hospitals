import requests
import bs4
import re
import csv

res = requests.get('https://www.myhospitals.gov.au/search/hospitals')
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, "html.parser")

# Finds all of the hospital class divs
divs = soup.find_all("div", class_="hospital-text pull-right")

# Build a list of all of the links to hospitals on the main search page
linkList = []  # Create a list to store the links to each hospital
for div in divs:  # Loop through each of the hospital divs and find the links
    links = div.find_all('a')
    for a in links:  # For each link, grab the href value and add it to the linkList
        linkList.append("https://www.myhospitals.gov.au/" + a['href'])

# Test orgs - use this to test example public and private hospitals
#linkList = ['https://www.myhospitals.gov.au/hospital/510700251/york-hospital',
#            'https://www.myhospitals.gov.au//hospital/PR69739N/albury-wodonga-private-hospital',
#            'https://www.myhospitals.gov.au/hospital/PR29946W/abbotsford-private-hospital']

# Set up the output file and writer
outFile = open('australia_orgs.csv', 'w', newline='')
outWriter = csv.writer(outFile)


# Define variables of interest for each hospital
group = ''  # Parent group (if private)
name = ''  # Hospital name
street = ''  # 1st line of address
state = ''  # 2nd line of address
phone = ''  # Phone number
web = ''  # Web address
beds = ''  # Bed size
pattern = re.compile(r'Member of')  # Used to determine if the hospital has a parent group

# print(linkList)
for link in linkList:
    res2 = requests.get(link)
    res2.raise_for_status()
    linkSoup = bs4.BeautifulSoup(res2.text, "html.parser")

    # Finds the name of the hospital
    head = linkSoup.find_all("h1")
    name = head[1].text  # Hospital name is the second h1 tag

    # Find all of the services that the hospital offers
    serviceList = []  # Store the services here
    data = linkSoup.find_all("div", class_="data-section")  # Services are stored in the data section div
    for li in data:  # loop through each list tag to find the services
        services = li.find_all('li')
        for service in services:
            serviceList.append(service.text)

    # Check the icon class to determine if the hospital is public or private
    if not linkSoup.find("div", class_='hospital-icon-inner-private-hospital'):
        type = 'Public'
    else:
        type = 'Private'
        group = linkSoup.find(text=pattern)

    # Find the bed size
    paras = linkSoup.find_all("p", class_="bold")
    for p in paras:
        beds = paras[2].text  # The 3rd  p tag contains the bed size

    # Finds the contact details for the hospital
    divs = linkSoup.find_all("div", class_="address pull-left")
    for p in divs:  # Loop through each p tag and get the contact details. Exceptions used as some fields are missing
        try:
            addr = p.find_all('p')
        except Exception:
            pass
        try:
            street = addr[1].text
        except Exception:
            pass
        try:
            state = addr[2].text
        except Exception:
            pass
        try:
            phone = addr[4].text
        except Exception:
            pass
        try:
            web = addr[5].find('a')
        except Exception:
            pass

    print(name, type, street, state, phone, web['href'], serviceList, beds[15::], group)  # Monitor progress
    outWriter.writerow([name, type, street, state, phone, web['href'], beds[15::], group, serviceList])

# Close the file
outFile.close()
