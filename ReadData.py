
import requests as re
import pandas as pd


#####################

# Session API
response = re.get("https://apigw.withoracle.cloud/formulaai/sessions")
sessionDf = pd.json_normalize(response.json())

trackId = 'Monza' # User input for final application

# Seprating out the df based on track id
selectedSessionDf = sessionDf[sessionDf['TRACKID'] == trackId]

# Appending the data for each session id and lap

# apending directly in data frame ~ 40 seconds
data = pd.DataFrame()
for index, row in selectedSessionDf.iterrows():
    laps = row.loc['LAPS']
    sessionId = row.loc['M_SESSIONID'] 
    # data should be upto lap number.. but we have data upto lap+1
    for i in range(laps+1):
        url = "https://apigw.withoracle.cloud/formulaai/trackData/" + sessionId + "/" + str(i+1)
        temp = pd.json_normalize(re.get(url).json())
        print("Session id- " + sessionId + " and Lap number- " + str(i+1)+ " data shape is- " + str(temp.shape)) 
        data = data.append(temp)
        

