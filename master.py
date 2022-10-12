# API Documentation = https://github.com/dtsong/sleeper-api-wrapper

from curses import keyname
from hashlib import new
import json
import csv
from numpy import sort_complex
import sleeper_wrapper
import statistics
import requests
import classes
import os
import shutil
import subprocess
import pandas as pd
from sleeper_wrapper import League
from sleeper_wrapper import User
import gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials

# Import Configuration Setttings
configobject = open("config_settings.json")
config_settings = json.load(configobject)

# Set Static Variables
league_id = config_settings["sleeperbot_league_id"]
discord_integration = config_settings["discord_notifications"]
google_integration = config_settings["google_sheets_integration"]
scriptdir = os.getcwd()

if discord_integration.lower() == "true" :
    discordurl = str(config_settings["discord_url"])
    botname = config_settings["discord_bot_name"]
    if "discord" in botname.lower() :
        print ("Discord bot name has the word discord which is not allowed, turning off discord notifications")
        discord_integration = "false"

if google_integration.lower() == "true" :
    spreadsheetname = config_settings["google_sheet_name"]
    shareemail = config_settings["google_sheet_share_email"]

# Get NFL State & Current Week
response = requests.get("https://api.sleeper.app/v1/state/nfl")
nflstate = response.json()
week = nflstate["week"]
currentweek = nflstate["week"]
lastweek = week - 1

getusers = requests.get("https://api.sleeper.app/v1/league/784654068411998208/users")
users = getusers.json()

# Get Roster & League Data that will be used in further defs
league = League(league_id)
rosters = league.get_rosters()
users = league.get_users()
standings = league.get_standings(rosters,users)
matchups = league.get_matchups(week)
object = classes.Statistics()

rosterdata = []
for roster in rosters :
    week = currentweek
    roster_id = roster["roster_id"]
    #print("starting process for ", roster_id)
    MedianRecord = object.get_medianrecord(roster_id, week, league)
    
    # Set Win/Loss Record for normal & median league
    medianwins = (MedianRecord[0])
    medianlosses = (MedianRecord[1])
    regwins = (roster["settings"]["wins"])
    reglosses = (roster["settings"]["losses"])
    combinedlosses = medianlosses + reglosses
    combinedwins = medianwins + regwins
    medianrecordstr = (str(combinedwins) + "-" + str(combinedlosses))
    regular_record_str = (str(regwins) + "-" + str(reglosses))

    # Starting Process to get Luck Rating, and league record
    count = lastweek
    seasonluck = 0
    totalluck = 0
    seasonleaguewins = 0
    seasonleaguelosses = 0

    while count > 0 :
        #print("Getting Luck Rating & League Rating")
        week = count
        matchups = league.get_matchups(week)
        
        record = object.get_league_week_record(roster_id, week, league, matchups)
        status = object.get_matchup_result(roster_id, week, league, matchups)
        wins = record[0]
        losses = record[1]
        luck = object.get_luck_rating(wins, losses, status)
        
        # Get Current Week data
        if count == lastweek :
            weekluck = luck
            weekleaguewins = record[0]
            weekleaguelosses = record[1]
        
        totalluck += luck
        seasonleaguewins += record[0]
        seasonleaguelosses += record[1]
        
        count -= 1
    
    # Get Points For/Aginst as well as average points for & against
    ptsfor = (roster["settings"]["fpts"])
    ptsaginst = (roster["settings"]["fpts_against"])
    avgptsfor = ptsfor / lastweek
    avgptsaginst = ptsaginst / lastweek

    # Build Record variables
    seasonluck = round(totalluck / lastweek)
    luck = round(weekluck)
    leaguerecordstr = (str(seasonleaguewins) + "-" + str(seasonleaguelosses))

    
    # Get User Data
    owner_id = roster["owner_id"]
    team_logo = ""
    team_name = ""
    for user in users :
        user_id = user["user_id"]
        if user_id == owner_id :
            team_name = user["display_name"]
            team_logo = user["avatar"]

    # Build JSON Values
    item = {"id": roster_id}
    item["roster_id"] = roster_id
    item["team_name"] = team_name
    item["ownerid"] = owner_id
    item["wins"] = regwins
    item["losses"] = reglosses
    item["record"] = regular_record_str
    item["med_wins"] = medianwins
    item["med_losses"] = medianlosses
    item["median_record"] = medianrecordstr
    item["com_wins"] = combinedwins
    item["com_losses"] = combinedlosses
    item["league_wins"] = seasonleaguewins
    item["league_losses"] = seasonleaguelosses
    item["league_record"] = leaguerecordstr
    item["pts_for"] = ptsfor
    item["pts_aginst"] = ptsaginst
    item["avg_pts_for"] = avgptsfor
    item["avg_pts_aginst"] = avgptsaginst 
    item["season_luck"] = seasonluck
    item["week_luck"] = luck

    # Appened all JSON Items into rosterdata
    rosterdata.append(item)

jsonData = json.dumps(rosterdata)

# Load Json
loaded = json.loads(jsonData)

# Serializing json
json_object = json.dumps(loaded, indent=4)
 
# Writing to week.json
week = lastweek
jsonfile = os.path.join(scriptdir, "output", "week%s-output.json" % week)
with open(jsonfile,"w") as outfile:
    outfile.write(json_object)

with open(jsonfile) as json_file:
    jsondata = json.load(json_file)

csvfile = os.path.join(scriptdir, "output", "week%s-output.csv" % week) 
data_file = open(csvfile, 'w', newline='')
csv_writer = csv.writer(data_file)
 
count = 0
for data in jsondata:
    if count == 0:
        header = data.keys()
        csv_writer.writerow(header)
        count += 1
    csv_writer.writerow(data.values())
 
data_file.close()

# Sort by median rankings
median_rankings_csv = os.path.join(scriptdir, "output", "week%s-MedianRankings.csv" % week) 
col_list = ["roster_id" , "team_name", "median_record", "com_wins", "com_losses", "pts_for", "pts_aginst"]
dataFrame = pd.read_csv(csvfile, usecols=col_list)
dataFrame.sort_values(["com_wins","pts_for"],axis=0, ascending=False,inplace=True,na_position='first')
dataFrame.to_csv(median_rankings_csv)

# Sort by avg_pts_for
avg_pts_for_csv = os.path.join(scriptdir, "output", "week%s-avgPtsForRankings.csv" % week) 
col_list = ["roster_id" , "team_name", "avg_pts_for", "pts_for", "pts_aginst"]
dataFrame = pd.read_csv(csvfile, usecols=col_list)
dataFrame.sort_values(["avg_pts_for"],axis=0, ascending=False,inplace=True,na_position='first')
dataFrame.to_csv(avg_pts_for_csv)

# Sort by luck
week_luck_csv = os.path.join(scriptdir, "output", "week%s-LuckRankings.csv" % week) 
col_list = ["roster_id" , "team_name", "week_luck"]
dataFrame = pd.read_csv(csvfile, usecols=col_list)
dataFrame.sort_values(["week_luck"],axis=0, ascending=False,inplace=True,na_position='first')
dataFrame.to_csv(week_luck_csv)

# Sort by season luck
season_luck_csv = os.path.join(scriptdir, "output", "week%s-SeasonLuckRankings.csv" % week) 
col_list = ["roster_id" , "team_name", "season_luck"]
dataFrame = pd.read_csv(csvfile, usecols=col_list)
dataFrame.sort_values(["season_luck"],axis=0, ascending=False,inplace=True,na_position='first')
dataFrame.to_csv(season_luck_csv)

# Sort by season league wins
league_record_csv = os.path.join(scriptdir, "output", "week%s-LeagueRecordRankings.csv" % week) 
col_list = ["roster_id" , "team_name", "league_record", "pts_for", "league_wins", "league_losses"]
dataFrame = pd.read_csv(csvfile, usecols=col_list)
dataFrame.sort_values(["league_wins", "pts_for"],axis=0, ascending=False,inplace=True,na_position='first')
dataFrame.to_csv(league_record_csv)

if discord_integration.lower() == "true" :
    message = ("Data for week " + str(lastweek) + " has finished processing.")
    title = ("Week "+ str(lastweek) + " automation")
    object.post_discord_message(discordurl, message, title, botname)

# Variables definition

# Dump Data to Google Sheets if integration is enabled
if google_integration.lower() == "true" :

    scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(credentials)

    # Set Worksheet Name Variables
    MedianRankingsWorkSheetName = "MedianRankings"
    AvgPtsForWorkSheetName = "AvgPtsForRankings"
    WeekLuckWorkSheetName = "WeekLuckRankings"
    SeasonLuckWorkSheetName = "SeasonLuckRankings"
    LeagueRankingsWorkSheetName = "LeagueRankings"
    WeeklySheetName = ("Week%s" % week)
    
    # Test if spreadsheet is created
    try :
        spreadsheet = client.open(spreadsheetname)
        createSpreadsheet = False
    except gspread.exceptions.SpreadsheetNotFound:
        print("Spreadsheet not found, attempting to create one")
        createSpreadsheet = True

    if createSpreadsheet == True :
        print("Creating spreadsheet as it was not found")
        spreadsheet = client.create(spreadsheetname)
        #spreadsheet.share(shareemail, perm_type='user', role='writer')
        spreadsheet = client.open(spreadsheetname)

    spreadsheetId = spreadsheet.id
    worksheet_list = spreadsheet.worksheets()
    print ("Printing List of worksheets")
    print (worksheet_list)

    # Checking to see if any worksheets need to be created, update worksheets afterwards
    if MedianRankingsWorkSheetName not in str(worksheet_list) :
        print("Count Not Find Median Rankings Sheet, creating sheet")
        spreadsheet.add_worksheet(title=MedianRankingsWorkSheetName, rows="1000", cols="20")
        print("Created Median Rankings, Updating the worksheet")
        spreadsheet.values_update(MedianRankingsWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(median_rankings_csv)))})
    else :
        print("Found Median Rankings, Updating the worksheet")
        spreadsheet.values_update(MedianRankingsWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(median_rankings_csv)))})

    if AvgPtsForWorkSheetName not in str(worksheet_list) :
        print("Count Not Find Average Points Sheet, creating sheet")
        spreadsheet.add_worksheet(title=AvgPtsForWorkSheetName, rows="1000", cols="20")
        print("Created Average Points Sheet, Updating the worksheet")
        spreadsheet.values_update(AvgPtsForWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(avg_pts_for_csv)))})
    else :
        print("Found Median Rankings, Updating the worksheet")
        spreadsheet.values_update(AvgPtsForWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(avg_pts_for_csv)))})

    if WeekLuckWorkSheetName not in str(worksheet_list) :
        print("Count Not Find WeekLuckRankings Sheet, creating sheet")
        spreadsheet.add_worksheet(title=WeekLuckWorkSheetName, rows="1000", cols="20")
        print("Created Week Luck Sheet, updating the worksheet")
        spreadsheet.values_update(WeekLuckWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(week_luck_csv)))})
    else :
        print("Found Week Luck Sheet, updating the worksheet")
        spreadsheet.values_update(WeekLuckWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(week_luck_csv)))})

    if SeasonLuckWorkSheetName not in str(worksheet_list) :
        print("Count Not Find SeasonLuckRankings Sheet, creating sheet")
        spreadsheet.add_worksheet(title=SeasonLuckWorkSheetName, rows="1000", cols="20")
        print("Created Season Luck Worksheet, updating worksheet")
        spreadsheet.values_update(SeasonLuckWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(season_luck_csv)))})
    else: 
        print("Found Season Luck Worksheet, updating worksheet")
        spreadsheet.values_update(SeasonLuckWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(season_luck_csv)))})

    if LeagueRankingsWorkSheetName not in str(worksheet_list) :
        print("Count Not Find SeasonLuckRankings Sheet, creating sheet")
        spreadsheet.add_worksheet(title=LeagueRankingsWorkSheetName, rows="1000", cols="20")
        print("Created League Rankings Worksheet, updating worksheet")
        spreadsheet.values_update(LeagueRankingsWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(league_record_csv)))})
    else: 
        print("Found League Rankings Worksheet, updating worksheet")
        spreadsheet.values_update(LeagueRankingsWorkSheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(league_record_csv)))})

    if WeeklySheetName not in str(worksheet_list) :
        print("Count Not Find Week Sheet, creating sheet")
        spreadsheet.add_worksheet(title=WeeklySheetName, rows="1000", cols="20")
        print("Created Week%s Worksheet, updating worksheet" % week)
        spreadsheet.values_update(WeeklySheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(csvfile)))})
    else: 
        print("Found Week%s Worksheet, updating worksheet" % week)
        spreadsheet.values_update(WeeklySheetName, params={'valueInputOption': 'USER_ENTERED'},body={'values': list(csv.reader(open(csvfile)))})
    



