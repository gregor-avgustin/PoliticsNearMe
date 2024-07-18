import string

from config import *

import requests
import json
import sqlite3
from datetime import datetime


# creates a new table with given city name if it doesn't exist in the database already
def createTable(cityName):
	connection = sqlite3.connect('cities.db')
	sqlCursor = connection.cursor()

	tempQuery = "CREATE TABLE IF NOT EXISTS '" + cityName + ("'("
															"Name TEXT, "
															"Start TEXT, "
															"End TEXT, "
															"Link TEXT,"
															"UNIQUE (Name))")

	sqlCursor.execute(tempQuery)

	connection.commit()
	sqlCursor.close()
	connection.close()


# calling the API to search for political events in given city
def searchInfo(cityName):
	querystring = {"query": ("Politics in " + cityName), "date": "any", "is_virtual": "false",
				   "start": "0"}

	headers = {
		"x-rapidapi-key": API_KEY,
		"x-rapidapi-host": HOST_NAME
	}

	url = "https://real-time-events-search.p.rapidapi.com/search-events"
	req = requests.get(url, headers = headers, params = querystring)

	return json.loads(req.text)


# parses the data that the API returns and uploads it into the database
def parseInfo(data, cityName):
	connection = sqlite3.connect('cities.db')

	sqlCursor = connection.cursor()

	for item in data["data"]:
		try:
			eventName = item["name"]
		except:
			eventName = "N/A"

		try:
			startTime = item["start_time"]
		except:
			startTime = "N/A"

		try:
			endTime = item["end_time"]
		except:
			endTime = "N/A"

		try:
			link = item["link"]
		except:
			link = "N/A"

		tempQuery = "INSERT OR IGNORE INTO '" + cityName + "' VALUES (?, ?, ?, ?)"
		sqlCursor.execute(tempQuery, (eventName, startTime, endTime, link))

	connection.commit()
	sqlCursor.close()
	connection.close()


# goes through the database and removes any events that are past the user's current data and time
def updateDates(cityName):
	connection = sqlite3.connect('cities.db')
	sqlCursor = connection.cursor()

	userTime = datetime.now()
	userTimeString = userTime.strftime("%Y-%m-%d %H:%M:%S")

	tempQuery = "DELETE FROM '" + cityName + "' WHERE Start<'" + userTimeString + "'"
	sqlCursor.execute(tempQuery)

	connection.commit()
	sqlCursor.close()
	connection.close()


# a function to print out the events that were found in the city through the API
def printEvents(cityName):
	print("\nHere are all the events occurring soon in " + string.capwords(cityName) + ":")
	connection = sqlite3.connect('cities.db')
	sqlCursor = connection.cursor()

	tempQuery = "SELECT * FROM '" + cityName + "'"
	eventsInfo = sqlCursor.execute(tempQuery)

	counter = 1
	outText = "Event {eventCounter}: "
	for event in eventsInfo:
		print(outText.format(eventCounter = counter), end = "")
		print(event)
		counter += 1

	sqlCursor.close()
	connection.close()

print("Want to learn more about politics in your city? Then this is the app for you!")
cityName = input("What city do you live in? ").lower()

createTable(cityName)

data = searchInfo(cityName)
parseInfo(data, cityName)

updateDates(cityName)

printEvents(cityName)
