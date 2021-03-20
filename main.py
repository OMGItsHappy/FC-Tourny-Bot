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
{"members" : {"member1" : {"startingKills" : int, 'endingKills' : int, 'startingBountie' : int, 'endingBountie' : int}}
 "kills" : {'starting' : int, 'ending' : int} These would just be ints if we follow the killsheet method as there would be no start/end
 "bounties" : {'starting' : int, 'ending' : int}
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
from typing import List
from customExcpetions import *
from collections import defaultdict
import json
import asyncio
import io

token = open('token.txt', 'r').readline()
intents = discord.Intents.all()
client = discord.Client(intents = intents)

def splitSpaces(inStr:str) -> List[str]:
	return [x for x in inStr.split(' ') if x != '']

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

@client.event
async def on_message(msg):
	if msg.author.id != client.user.id:
		msgParsed = splitSpaces(msg.content)
		if msgParsed[0] == '=reg':
			teamsJSON = await on_ready()
			teamsJSON = defaultdict(None, teamsJSON)
			try:
				teamate = await msg.guild.fetch_member(int(msgParsed[1].strip('!<>@')))
				if teamate == discord.NotFound:
					raise noTeamate
				if len(teamsJSON) < 1:	teamsJSON['1']['members'] = [msg.author.id, teamate]
				else:	teamsJSON[max(teamsJSON) + 1]['members'] = [msg.author.id, teamate]
				
				def check(checkMsg):
					return checkMsg.author == msg.author and checkMsg.isdigit()
				try:
					kills = await client.wait_for('message', check = check, timeout = 60.0)
				except asyncio.TimeoutError:
					await msg.channel.send('Please')
			except noTeamate:
				msg.channel.send('You did not mention your teamate when registering for a team.')


client.run(token)

try:
	if True:
		pass
		raise bad('hi')
except bad as e:
	print(e)
