import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import json
import numpy as np

import pandas as pd


#Helper Functions
def timeToMilis(num):
	time = num.split(":")
	if(len(time) == 1):
		return int(float(time[0]) * 1000)
	return int((float(time[0]) * 60 + float(time[1])) * 1000)

def formatDigit(num ):
	if(num < 10 ):
		return "0" + str(num)
	return str(num)

def postProcess(df):
	df['YearMonth'] = df['Date'].map(lambda x: str(x.year) + "-" + formatDigit(x.month))
	return df


#File import statements
def extractCSTimer(times , sessionID):
	for time in times:
	   output = json.loads(time)

   
	#Extract lists for penalty, time, scramble and date
	if(sessionID is None):
		sessionID = list(output.keys())[0]

	print("sessionID:" , sessionID)
	results = list(zip(*output[sessionID]))


	#seperate penalty and time
	out2 = list(zip(*results[0]))


	#put them in dataframe
	df = pd.DataFrame({"Penalty": out2[0] , "Time": out2[1]})


	#Get total time using function
	def totalTime(row):
		if(row["Penalty"] >= 0):
			return row["Penalty"] + row["Time"]
		else:
			return -1
	df["TotTime"] = df.apply(totalTime , axis=1)


	#Complete df
	df["Scramble"] = results[1]
	df["Date"] = results[3]

	def toDatetime(time):
		return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
	df["Date"] = pd.to_datetime(df["Date"].apply(toDatetime))

	return df


def extractTwistyTimer(times):
	arr = {"TotTime": [] , "Scramble": [] , "Date" :  []}
	with open("times.txt") as times:
		for time in times:
			parts = time.split(";")
			arr["TotTime"].append(timeToMilis(parts[0].strip('\"')))
			arr["Scramble"].append(parts[1].strip('\"'))
			arr["Date"].append(parts[2].strip("\n").strip('\"'))
	

	df  = pd.DataFrame(arr)
	df["Date"] = pd.to_datetime(df["Date"])
	return df

def getData(contents , fileSource , sessionID):
	try:
		content_type, content_string = contents.split(',')
		decoded = base64.b64decode(content_string)
		times = io.StringIO(decoded.decode('utf-8'))
		if fileSource == "CSTimer":            
			df = extractCSTimer(times , sessionID)
		else:
			df = extractTwistyTimer(times)
			

		df = postProcess(df)
		return df

	except Exception as e:
		print(e)
		raise e


#assumes data comes in JSON format #TODO support all formats
def getColumnNames(contents):
	try: 
		content_type, content_string = contents.split(',')
		decoded = base64.b64decode(content_string)
		times = io.StringIO(decoded.decode('utf-8'))
		for time in times:
			output = json.loads(time)
		return list(output.keys())
	except Exception as e:
		print(e)
		raise e

