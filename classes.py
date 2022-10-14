from numpy import var
from hashlib import new
import json
import sleeper_wrapper
import statistics
import requests
import classes
import pandas as pd
from sleeper_wrapper import League
import gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials

class Statistics ():

    def get_medianrecord(self, roster_id, week, league) :
        medianwins = 0
        medianlosses = 0
        while week > 0 :
            #print("Starting Process for week", week)
            matchups = league.get_matchups(week)

            medianscores = []
            for matchup in matchups :
                score = matchup["points"]
                medianscores.append(score)

            median = (statistics.median(medianscores))
            
            #print("Median for week", week, " is ", median)

            for matchup in matchups :
                points = matchup["points"]
                matchuprosterid = matchup["roster_id"]
                if matchuprosterid == roster_id :
                    if points < median :
                        medianlosses += 1
                    if points > median :
                        medianwins += 1

            week -= 1
        return (medianwins, medianlosses)

    def get_league_week_record(self, roster_id, week, league, matchups):
        #print("Starting Process for week", week)
        #matchups = league.get_matchups(week)

        # Set def values
        leagueloss = 0
        leaguewin = 0
        scores = []
        myscore = ""

        for matchup in matchups :
            score = matchup["points"]
            scores.append(score)

        for matchup in matchups :
            if matchup["roster_id"] == roster_id :
                myscore = matchup["points"]

        for score in scores :
            if score != myscore :
                if score > myscore :
                    leagueloss += 1
                if score < myscore :
                    leaguewin += 1
        return (leaguewin, leagueloss)

    def get_matchup_result(self, roster_id, week, league, matchups) :

        #matchups = league.get_matchups(week)
        matchupid = 0
        theirscore = 0
        myscore = 0
        
        # Get the matchup ID that equals to the roster_id were testing
        for matchup in matchups :
            if matchup["roster_id"] == roster_id :
                matchupid = matchup["matchup_id"]
        
        # Get Their Score by matching matchup ID and then getting points
        for matchup in matchups :
            if matchup["matchup_id"] == matchupid :
                if matchup["roster_id"] != roster_id :
                    theirscore = matchup["points"]
        
        # Get Score for the roster ID set for this function
        for matchup in matchups :  
            if matchup["matchup_id"] == matchupid :  
                if matchup["roster_id"] == roster_id :
                    myscore = matchup["points"]
            
        if myscore > theirscore :
            return ("win")
        if myscore < theirscore :
            return ("loss")

    def get_luck_rating (self, wins, losses, status) :
        #set vars
        luck = 0
        percent = 0
        if status == "win" :
            luck = losses/11
            percent = luck * 100
        if status == "loss" :
            luck = wins/11
            percent = -(luck * 100)
        return (percent)

    def get_sos(self, roster_id, week, league, matchups) :

        #matchups = league.get_matchups(week)
        print("starting get_sos function")
        matchupid = 0
        theirscore = 0
        myscore = 0
        scoresobject = []
        matchrank = 0

        # Get the matchup ID that equals to the roster_id were testing
        for matchup in matchups :
            if matchup["roster_id"] == roster_id :
                matchupid = matchup["matchup_id"]

        # Get Their Score by matching matchup ID and then getting points
        for matchup in matchups :
            if matchup["matchup_id"] == matchupid :
                if matchup["roster_id"] != roster_id :
                    theirscore = matchup["points"]
        
        # Get Score for the roster ID set for this function
        for matchup in matchups :  
            if matchup["matchup_id"] == matchupid :  
                if matchup["roster_id"] == roster_id :
                    myscore = matchup["points"]
        
        for matchup in matchups :
            if matchup["points"] != myscore :
                scoresobject.append(matchup["points"])
        
        scores = sorted(scoresobject)
        
        for item in scores :
            if item == theirscore :
                print(item)
                matchrank = scores.index(item)
                print (matchrank)

        return matchrank
    
    def post_discord_message(self, discordurl, message, title, botname) :
        #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
        data = {
            "username" : botname
        }

        #leave this out if you dont want an embed
        #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
        data["embeds"] = [
            {
                "description" : message,
                "title" : title
            }
        ]

        result = requests.post(discordurl, json = data)

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))

    def ImportCsv_to_Google(csvFile, sheet, cell):

        # csvFile - path to csv file to import
        # sheet - a gspread.Spreadsheet object
        # cell - string giving starting cell, optionally including sheet/tab name
        # ex: 'A1', 'Sheet2!A1', etc.

        if "!" in cell:
            (tabName, cell) = cell.split("!")
            wks = sheet.worksheet(tabName)
        else:
            wks = sheet.sheet1
        (firstRow, firstColumn) = gspread.utils.a1_to_rowcol(cell)

        with open(csvFile, "r") as f:
            csvContents = f.read()
        body = {
            "requests": [
                {
                    "pasteData": {
                        "coordinate": {
                            "sheetId": wks.id,
                            "rowIndex": firstRow - 1,
                            "columnIndex": firstColumn - 1,
                        },
                        "data": csvContents,
                        "type": "PASTE_NORMAL",
                        "delimiter": ",",
                    }
                }
            ]
        }
        return sheet.batch_update(body)
    
    def get_trade_value(self) :
        print("Future value ideas for trades")
        # Get each team in the trade
        # Get their positions that they traded away & traded for
        # Get Average Points at those positions before & after trade
        # Output total gain/loss after comparing before and after of each positon
    
    def get_avg_pts_at_position_starters (self, roster_id, position, matchups) :
        print("Get each teams average points per game at a position")
        # Get all players in starters list
        # filter by position 
        # get average
    
    def get_avg_pts_at_position_bench (self, roster_id, position, matchups) :
        print("Get each teams average points per game at a position")
        # Get all players in bench list
        # filter by position 
        # get average


    """
    def get_league_record(self, roster_id, week, league):
        wins = 0
        losses = 0
        while week > 0 :
            record = get_league_week_record(self, roster_id, week, league)
            wins += record[0]
            losses += record[1]
            week -= 1
        return (wins, losses)
    """
