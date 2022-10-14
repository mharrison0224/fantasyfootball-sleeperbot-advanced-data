![GitHub issues](https://img.shields.io/github/issues/mharrison0224/fantasyfootball-sleeperbot-advanced-data)
![GitHub forks](https://img.shields.io/github/forks/mharrison0224/fantasyfootball-sleeperbot-advanced-data)
![GitHub stars](https://img.shields.io/github/stars/mharrison0224/fantasyfootball-sleeperbot-advanced-data)
![GitHub license](https://img.shields.io/github/license/mharrison0224/fantasyfootball-sleeperbot-advanced-data)
# fantasyfootball-sleeperbot-advanced-data

This repo is a simple python script that will pull in your league data from sleeperbot and build out some more advanced data sets to be used however. 
I'm a very noob python developer, the code looks like a$$ but it works lmao

This program will output the following data:

1. Weekly Luck Rating
2. Season Luck Rating
3. League Record (calcuation ran where you matchup against every league mate every week to see how you stack up overall)
4. Median Record (calculate league standings if you enabled the league median)
5. Average Point For (points for / weeks played)
6. Average Points Aginst (points against / weeks played)
7. Calculates strenght of schedule (opponent score ranked 0-X (x = managers - 1) over the season

The output will go into the project folder \ output folder where its sorted by week in a .csv file extention to easily open with notepad, excel, or google sheets.

## Installation

1. Download the github repository, save the zip file in any location
2. Right Click the zip file, extract to any location you'd like
3. Open any web browser, and go to here: https://www.python.org/downloads/
4. Download and install python
5. Open the fantasyfootball-sleeperbot-metrics folder (this is the folder you unzipped)
6. From fantasyfootball-sleeperbot-metrics folder, open the "install.bat" file to install the required python packages

## Update Program with Sleeperbot League ID

This section will show you how to set the config_settings.json file. 

The config_settings.json file is where you put in your league specific data as well as enabling features such as google sheets integration or discord notifications

1. Browse to https://sleeperbot.com
2. Open your league you'd like to run reports on
3. The league id is in the url example: (https://sleeper.com/leagues/7846512124111998208/team) ex: league id is: 7846512124111998208
4. Open config_settings.json file with notepad
5. Replace "replace_with_League_ID" with "yourLeagueID" (in this example it would look this this: "7846512124111998208")
6. Save config_settings.json (make sure you save it with the same name, and in the project folder you opened it from)

## Enabling Discord Notifications

This section will detail how to enable discord notifications

1. Open discord, and open the server you'd like notifications to arrive
2. Under Text Channels, select the Edit Channel optiion (gear icon)
3. Select Integrations > View Webhooks > New Webhook
4. Select the "Copy the Webhook URL" button
5. Save Changes
6. Open the config_settings.json file
7. Replace "replace_with_discord_webhook" with "webhook url you copied from step 4"
8. Find the line that says "discord_notifications"
9. Replace false with true
10. Discord notifications are now enabled


## Enabling Google Sheets Data Output

If you want the script to update a google sheet, this section will detail how to do that

1. [Create credentials in Google API Console](http://gspread.readthedocs.org/en/latest/oauth2.html)
2. Download & Save the credentials.json file to the project folder
3. Find the line that says "google_sheets_integration"
4. Replace false with true
5. Create a google sheet, share the sheet with your API Credential account
6. Get the sheet ID from the url
7. Fine the  line that says "google_sheets_id"
8. Replace "google_sheet_id" with the ID you copied from the URL of the google sheet

## How to Run

1. Browse to folder location
2. Double Click RunMe.bat

or 

1. Open command prompt
2. CD C:\Location_Of_Project
3. Type in the following command
```bash
  python master.py
```
