"""
Need a teams system with easy registration
Hopefully looks something like `=reg @{teamate} {optional team name}
If we are doing sheet system we need a questionare that asks them for kills, bountie tokens extracted, and a image of that killsheet
If we are using the leaderboard system we need a command for their starting kills and a command with their ending kills, likely in a similar questionare format.
`=start -> ask total kills -> {Entered integer} -> ask total bountie tokens extracted -> {entered integer} -> ask for screenshot of learderboard -> sent image -> add team to live team tracker
This format would be used for killsheets as well.
Hopefully have a way to start and end events
Hopefully have a way to automatically build a questionare [hard!]
Have a way to manually refresh scoreboard and update teams
Have a way to subtract from team kills, bounties, total score.
Way to clear all teams and scores
Possibly have people set start times.

Data structure will look like
{"members" : {"member1" : {"startingKills" : int, 'endingKills' : int, 'startingBountie' : int, 'endingBountie' : int, 'startingUpdated' : int, 'endingUpdated' : int}}
 "score" : int
}
"""

"""
Date time retrevial.
import PIL.Image
import os
from datetime import datetime
10800
print(datetime.fromtimestamp(os.stat(r'D:\Downloads\Screenshot 2021-03-19 231054.png').st_ctime))
"""

import discord
from typing import List, Optional
from customExcpetions import *
from collections import defaultdict
import json
import asyncio
import io
from datetime import datetime

token = open('token.txt', 'r').readline()
intents = discord.Intents.all()
client = discord.Client(intents = intents)

def splitSpaces(inStr:str) -> List[str]:
	return [x for x in inStr.split(' ') if x != '']

def findUserTeam(inputJSON : dict, inputID : str) -> Optional[str]:
	"""  Finds a users teams and return their team number, If a user is not in a team it will return None """
	return next((team for team in inputJSON 
							 for member in inputJSON[team]['members'] 
							 if inputID == member), None)

@client.event
async def on_ready():
	"""Need to check if the teams json exists, if it dosnt we need to construct it"""
	try:
		teamsFile = open('teamsFile.json', 'r')
		try:
			teamsJSON = json.load(teamsFile)
		except io.UnsupportedOperation:
			teamsJSON = defaultdict()
			json.dump(teamsJSON, open('teamsFile.json', 'w'))
	except (FileNotFoundError, json.decoder.JSONDecodeError):
		teamsFile = open('teamsFile.json', 'w')
		try:
			teamsJSON = json.load(teamsFile)
		except io.UnsupportedOperation:
			teamsJSON = defaultdict()
		json.dump(teamsJSON, teamsFile)
	finally:
		teamsFile.close()
	return teamsJSON

teamsJSON = await on_ready()
teamsJSON = defaultdict(None, teamsJSON)
teamsFile = open('teamsFile.json', 'w')

@client.event
async def on_message(msg):
	if msg.author.id != client.user.id:
		msgParsed = splitSpaces(msg.content)
		if msgParsed[0] == '=reg':
			try:
				teamate = await msg.guild.fetch_member(int(msgParsed[1].strip('!<>@')))
				if teamate == discord.NotFound:
					raise noTeamate
				if len(teamsJSON) < 1:	teamsJSON['1']['members'] = [msg.author.id, teamate]
				else:	teamsJSON[max(teamsJSON) + 1]['members'] = [msg.author.id, teamate]

				json.dump(teamsJSON, teamsFile)
				
			except noTeamate:
				msg.channel.send('You did not mention your teamate when registering for a team.')
		
		if msgParsed[0] == '=start':
			try:
				userTeam = findUserTeam(teamsJSON, str(msg.author.id))
				if userTeam == None: raise noTeam

				if teamsJSON[userTeam]['members'][str(msg.author.id)]['startingBountie'] != '' or teamsJSON[userTeam]['memebers'][str(msg.author.id)]['startingKills'] != '': 
					def yes(checkMsg): return 'yes' in checkMsg.lower(), checkMsg:

					double = await msg.channel.send('You have already entered scores, are you sure you want to enter them again? type yes to continue')
					check1 = await client.wait_for("message", check = yes, timeout=20)

					double.delete()
					check1[1].delete()

					if not check1: raise stop

				def check(checkMsg):
					return checkMsg.author == msg.author and checkMsg.isdigit()

				sentBountie = msg.channel.send('Please type your total bountie score. It is your statistics {input the two ss\'s}')

				bountie = await client.wait_for('message', check = check, timeout = 60.0)

				sentKills = msg.channel.send('Please send your total kills total. {input the two ss\'s}')

				kills = await client.wait_for('message', check = check, timeout = 60.0)

				teamsJSON[userTeam]['members'][str(msg.author.id)]['startingBountie'] = bountie
				teamsJSON[userTeam]['members'][str(msg.author.id)]['startingKills'] = kills
				teamsJSON[userTeam]['edits'].append({'type' : 'Intial stats', 'time' : datetime.now().st_ctime, 'user' : msg.author.id})
				teamsJSON[userTeam]['score']['start'] = kills + (bountie%100)

				json.dump(teamsJSON, teamsFile)
        
				#check to see if other user has already added stats, if not we ping them reminding them to add stats
				otherUser = next((member for member in teamsFile[userTeam]['members'] if member != str(msg.author.id)))
				if teamsFile[userTeam][otherUser]['startingKills'] == '':
					msg.channel.send(f'<@!{otherUser}> please add your starting stats!')

			except asyncio.TimeoutError:
				await msg.channel.send('Please try and input starting scores again.')
			
			except noTeam:
				await msg.channel.send("Please join a team to use this functionality")

			except stop:
				pass

		if msgParsed[0] == '=end':
			try:
				userTeam = findUserTeam(teamsJSON, str(msg.author.id))
				if userTeam == None: raise noTeam

				if teamsJSON[userTeam]['members'][str(msg.author.id)]['endingBountie'] != '' or teamsJSON[userTeam]['memebers'][str(msg.author.id)]['endingKills'] != '': 
					def yes(checkMsg): return 'yes' in checkMsg.lower(), checkMsg:

					double = await msg.channel.send('You have already entered scores, are you sure you want to enter them again? type yes to continue')
					check1 = await client.wait_for("message", check = yes, timeout=20)

					double.delete()
					check1[1].delete()

					if not check1: raise stop

				sentBountie = msg.channel.send('Please type your total bountie score. It is your statistics {input the two ss\'s}')

				bountie = await client.wait_for('message', check = check, timeout = 60.0)

				sentKills = msg.channel.send('Please send your total kills total. {input the two ss\'s}')

				kills = await client.wait_for('message', check = check, timeout = 60.0)

				teamsJSON[userTeam]['members'][str(msg.author.id)]['endingBountie'] = bountie
				teamsJSON[userTeam]['members'][str(msg.author.id)]['endingKills'] = kills
				teamsJSON[userTeam]['edits'].append({'type' : 'Intial stats', 'time' : datetime.now().st_ctime, 'user' : msg.author.id})
				teamsJSON[userTeam]['score']['start'] = kills + (bountie%100)

				json.dump(teamsJSON, teamsFile)
				
				#check to see if other user has already added stats, if not we ping them reminding them to add stats
				otherUser = next((member for member in teamsFile[userTeam]['members'] if member != str(msg.author.id)))
				if teamsFile[userTeam][otherUser]['endingKills'] == '': msg.channel.send(f'<@!{otherUser}> please add your ending stats!')

			except asyncio.TimeoutError:
				await msg.channel.send('Please try and input scores again.')
			
			except noTeam:
				await msg.channel.send("Please join a team to use this functionality")

			except stop:
				pass

		if msgParsed[0] == '=edits':
			try:
				team = findUserTeam(teamsJSON, msg.author.id)
				if team == None: raise noTeam
				embed = discord.Embed(title = f'Team {team} edits to their stats')
				for edits in teamsJSON[team]['edits']:
					embed.add_field(name = edits['user'], value = f"{edits['time']}cst, Changed {edits['type']}")
				msg.channel.send(embed = embed)
			except noTeam:
				msg.channel.send('User is not in team')

client.run(token)

