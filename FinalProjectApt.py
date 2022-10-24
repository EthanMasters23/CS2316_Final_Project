# CS2316 Final Project 

import requests, re
from pprint import pprint
from bs4 import BeautifulSoup
import csv
from urllib.request import urlopen
import json
import ast

#reading excel files
import xlwings as xw

# beautifulSoup byt for XML
import xml.etree.ElementTree as Et

# Data Visualization
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

#writing data to a pickle file
import pickle

#pandas
import pandas as pd

###############################################################################################################################################

# Apartments.com script for webscraping by city

#used to mask webrequest
userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"

# This is my base url I'll pass through cities as a string into the url to obtain data for apartments in that city
# url2 = f"https://www.apartments.com/{city_string}/"

############################################################### HOW TO MAKE CITY STRING FOR APARTMENTS.COM

# State and Abbreviation
# I webscared a gov website to obtain state abbreviations and state names so that I can easily subsitute names when I make my city string example string: "chicago-il"
stateID = {key[0]:key[1] for key in [[id.text.strip() for id in state.find_all('td')] for state in BeautifulSoup(requests.get("https://www.ssa.gov/international/coc-docs/states.html",headers={"User-Agent":f'{userAgent}'}).text, "html.parser").find_all("tr")]}

# I wrote this data to a excel file so I don't need to webscarpe each time I run my file in order to decrease runtime and be more efficient
# stateID data frame and writing to excel
# stateDataFrame = pd.DataFrame(stateID)
# stateDataFrame.to_excel('./StateIDXLSX.xlsx', index=False)
# pprint(stateDataFrame)

# I also copyed stateID information into pkl file to no longer need webscraping to have the option of both pickle files stores data exactly as a dicitonary therefore easier to call from (just to have multiple options)
# file = open("stateID_data.pkl", "wb")
# pickle.dump(stateID, file)
# file.close()
# file = open("stateID_data.pkl", "rb")
# output = pickle.load(file)
# file.close()

# I collected population data from the census per city from a csv file I downloaded from the census.gov this way I can sort cityList by population
cityListData = [{"City":value[8],"State":value[9],"Population":value[10]} for value in list(csv.reader(open("UScityData.csv", encoding="utf8", errors='ignore')))[1:] if value[10].isdigit() if "County" not in value[8] if value[8].upper() not in stateID]
# pprint(cityListData)

#CityList sorted to find most populated or least populated cities
cityListDataSorted = sorted(cityListData, key=lambda x: int(x["Population"]), reverse=True)[:2000] # this slicing on the end will determine how many cities I webscrape
# print(len(cityListDataSorted))
# pprint(cityListDataSorted)

########Putting everyhting above together

# (data cleaning) because I didn't want to hardcode my cities I take the cities from my census data and convert them into a string with the right format ex output: "chicago-il"
finalCityList = list(set([re.sub(r" \(.*\)","",city["City"].lower()) + "-" + stateID[city["State"].upper()].lower() for city in cityListDataSorted]))
# pprint(len(finalCityList))
# pprint(finalCityList)

############################################################## HOW TO MAKE CITY STRING FOR APARTMENTS.COM (END)

#prints the dictionary containing all data
#BEST ONE this is a oneliner that will webscrape and pull all relevant info from apartment.com per city but for large cityList requests apartments.com may not offer apartments in that city so it will error so I use a for loop on line 64 to do try and except
# {city.upper():[[condo.find("span",{"class":"js-placardTitle title"}).text.strip(),condo.find("p",{"class":"property-pricing"}).text.strip()] for condo in BeautifulSoup(requests.get(f"https://www.apartments.com/{city}/",headers={"User-Agent":f'{userAgent}'}).text, "html.parser").find_all("li",{"class":"mortar-wrapper"})] for city in finalCityList}

# This is a one liner that not only parses through a city on apartments.com, but also parses through the pages within a city on apartments.come ex url for page 1 and 2: apartments.com/chicago-il/1, then apartments.com/chicago-il/2
# pprint([[[[condo.find("span",{"class":"js-placardTitle title"}).text.strip(),condo.find("p",{"class":"property-pricing"}).text.strip()] for condo in BeautifulSoup(requests.get(f"https://www.apartments.com/chicago-il/{page}",headers={"User-Agent":f'{userAgent}'}).text, "html.parser").find_all("li",{"class":"mortar-wrapper"})] for page in range(int(link.text.strip()[-2:]))] for link in BeautifulSoup(requests.get(f"https://www.apartments.com/chicago-il/",headers={"User-Agent":f'{userAgent}'}).text, "html.parser").find("span",{"class":"pageRange"})])

# This is a testList if you uncomment this line you will only run my webscraping for the cities below it's a good way to see apartment data from large cities with a lot of data
# finalCityList = ["chicago-il", "atlanta-ga", "seattle-wa", "san diego-ca", "baltimore-md", "dallas-tx", "philadelphia-pa", "houston-tx"]

# final code for webscraping all cities in the US for apartment data
####### START
outputDict = {}
noResponseList = []
responseList = []
pageDict = {}
for city in finalCityList: 
    print(city)
    cityList = []
    try:
        # intitial web request to pull the range of pages per city on apartments.com
        for link in BeautifulSoup(requests.get(f"https://www.apartments.com/{city}/",headers={"User-Agent":f'{userAgent}'}).text, "html.parser").find("span",{"class":"pageRange"}):
            # now we're interating through the rage of pages
            for page in range(int(re.search(r" (\d+$)",link.text.strip()).group(1))): # added regex statement see if it works
                try:
                    # now webscraping all apartment pricing and names
                    cityList += [[condo.find("span",{"class":"js-placardTitle title"}).text.strip(),condo.find("p",{"class":"property-pricing"}).text.strip()] for condo in BeautifulSoup(requests.get(f"https://www.apartments.com/{city}/{page}",headers={"User-Agent":f'{userAgent}'}).text, "html.parser").find_all("li",{"class":"mortar-wrapper"})]
                    responseList += [city]
                except:
                    try:
                        #accounting for a city name not matching the url city name for apartments.com
                        city = re.sub(r" city","",city)
                        city = re.sub(r" ",r"-",city)
                        cityList += [[condo.find("span",{"class":"js-placardTitle title"}).text.strip(),condo.find("p",{"class":"property-pricing"}).text.strip()] for condo in BeautifulSoup(requests.get(f"https://www.apartments.com/{city}/{page}",headers={"User-Agent":f'{userAgent}'}).text, "html.parser").find_all("li",{"class":"mortar-wrapper"})]
                        responseList += [city]
                    except:
                        #getting an dictionary containing the pages that cities on apartments.com started producing errors usually starting at around page 20 per city because those renters on that page don't have pricing or apartment names which is what I'm pulling
                        print(page) # I usually keep print(page) because it shows me the code is still running because it does take a long time to run with a larger finalCityList input
                        if city in pageDict:
                            pageDict[city] += [page]
                        else:
                            pageDict[city] = [page]
    except:
        print(f"page range request didn't even work for {city}") # this tells you what cities probably aren't supported by apartments.com or if they don't have pages
    if cityList:
        outputDict[city.upper()] = cityList 
    else: noResponseList += [city]

noResponseList = set(noResponseList) # taking care of diplicate cities
responseList = set(responseList) # taking care of duplicate cities

pprint("Length of pageDict:") # pageDictionary tells me what pages for my url request produced errors and how many are unaccounted for
pprint(len(pageDict))
pprint("Length of finalCityList:") # this is how many cities were attempted to be webscraped
pprint(len(finalCityList))
pprint("Length of outputDict:") # this tells me how many cities were webscraped actually
pprint(len(outputDict))
pprint("Length of noResponseList:") # This tells me the number of responses that errored in other words how many cities didn't responded
pprint(len(noResponseList))
pprint("Length of responseList:") # this tells me the number of cities that responded to my webscraping
pprint(len(responseList))

#### END

############### love this (converting to pandas data frame and easily writing to excel and csv file and easily read back)

# # pageDict data frame
pf = pd.DataFrame.from_dict(pageDict, orient='index')
pf = pf.transpose()

# # outputDict data frame
df = pd.DataFrame.from_dict(outputDict, orient='index')
df = df.transpose()

# #reading and writing to excel love it

pf.to_excel('./PageDictionaryXLSX.xlsx', index=False)

# #reading and writing to excel love it
df.to_excel('./FinalProjectXLSX.xlsx', index=False)
# df_dict = pd.read_excel("FinalProjectXLSX.xlsx", index_col=False)
# # df_dict = df_dict.reset_index(drop=True)
# # df_dict = df_dict.to_dict("list")
# # pprint(df_dict)

# #writing and reading csv file beautiful
df.to_csv('FinalProjectCSV.csv', index=False)
# dataFrame = pd.read_csv("finalprojectCSV.csv")
# dataFrame = dataFrame.to_dict("list")
# pprint(dataFrame)

# # writing outputDict data to pkl file to parse through easily
file = open("FinalProjectPickle.pkl", "wb")
pickle.dump(outputDict, file)
file.close()
# file = open("dictionary_data.pkl", "rb")
# output = pickle.load(file)
# file.close()

# ########## writing data to a file continued

# # No response data output
with open("noResponseListCity.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["City List (non-responsive)"])
    for city in noResponseList:
        writer.writerow([city])

# # Response data output
with open("responseListCity.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["City List (responsive)"])
    for city in responseList:
        writer.writerow([city])

############################################################################################ This is what I have so far for webscraping



############################################################################################# START DATA VISUALIZATION
# 
# This is what I have for data visualization for the data collected above through webscraping !!

# So, I have my finalProject data which is all my apartment data I collected per city
# For my first data visualition I'm creating a Choropleth Map of the US
# I have to collect apartment prices per STATE, so I iterate through my FinalProject data file after I convert it to a Pandas Data Frame and added apartment prices per STATE

df = pd.read_excel("FinalProjectXLSX.xlsx", index_col=False) # Reading my excel file with the city and apartment data
newDict = {}
for column in df:
    for price in df[df[column].notnull()][column]: # cleaning data and only iterating through values that are not NaN (null)
        res = ast.literal_eval(price) # Okay, so when I wrote my dataFrame to my excel file it stored my lists as string lists so here I'm converting the string list to an actual list
        if re.search(r"-(\w*)$",column).group(1) not in newDict: # checking if state exists in my dictionary already or if i need to intiate the key
            try:
                res = res[1]
                if "/mo" in res: # data cleaning 
                    res = re.sub(" /mo","",res)
                tuple = re.search(r"\$(.*) - (.*)",res).group(1,2) # grouping price range ex. "$1,203 - 1,023"
                apartment_value = re.sub(",","",tuple[0]) #index on zero for min apartment price
                newDict[re.search(r"-(\w*)$",column).group(1)] = [int(apartment_value)]
            except:
                res = res[1]
                if "$" in res:
                    if "/mo" in res:
                        res = re.sub(" /mo","",res)
                    value = re.search(r"\$(.*)",res).group(1)
                    apartment_value = re.sub(",","",value)
                    newDict[re.search(r"-(\w*)$",column).group(1)] = [int(apartment_value)]
                else:
                    pass
        else: # This is if the state key already exists in my dictionary and does the same thing as the if block if it is except for += instead of just = 
            try:
                res = res[1]
                if "/mo" in res:
                    res = re.sub(" /mo","",res)
                tuple = re.search(r"\$(.*) - (.*)",res).group(1,2)
                apartment_value = re.sub(",","",tuple[0]) #index on zero for min apartment price
                newDict[re.search(r"-(\w*)$",column).group(1)] += [int(apartment_value)]
            except:
                res = res[1]
                if "$" in res:
                    if "/mo" in res:
                        res = re.sub(" /mo","",res)
                    value = re.search(r"\$(.*)",res).group(1)
                    apartment_value = re.sub(",","",value)
                    newDict[re.search(r"-(\w*)$",column).group(1)] += [int(apartment_value)]
                else:
                    pass

dataFrame = pd.DataFrame.from_dict(newDict,orient='index') # converting dictionary into dataFrame, and have to do orient="index" because the array lengths are different !!
dataFrame = dataFrame.transpose()

dataFrame2 = dataFrame.mean() # Finding the average of apartment prices per state
dataFrame2 = dataFrame2.to_frame() # it was changed into a series because I did .mean() so now I can convert back to a dataFrame
dataFrame2.reset_index(inplace=True) # adding an index column so I can generate my Choropleth Map of the US
dataFrame2.columns = ["STNAME", "apartment_avg"] # creating headers so I can call on them in my figure
# print(dataFrame2)

# creating my Choropleth Map
fig = go.Figure(data=go.Choropleth(
    locations=dataFrame2["STNAME"], # Spatial coordinates
    z = dataFrame2['apartment_avg'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Blues',
    colorbar_title = "Thousands USD",
))

fig.update_layout(
    title_text = 'US Avg Aparement Prices',
    geo_scope='usa', # limite map scope to USA
)

fig.show()

################################################################################################################ END DATA VISUALIZATION
