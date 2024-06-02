from .utils import *

def liveTimingDataF1Handler(self, msg):
	compoundSymbol=self.msgStyle["compoundSymbol"]
	self.timingDataF1 = updateDictDelta(self.timingDataF1, msg["A"][1])
	for RacingNumber, stat in msg["A"][1]["Lines"].items():
		info = self.driverList[RacingNumber]
		if (
			"BestLapTime" in stat
			and "LastLapTime" in stat
			and "PersonalFastest" in stat["LastLapTime"]
			and stat["LastLapTime"]["PersonalFastest"] == True
		):
			# Get current tyre compound
			currentStint=self.tyreStintSeries['Stints'][RacingNumber][-1]
			if currentStint['Compound'] in compoundSymbol:
				currentCompound = f"{compoundSymbol[currentStint['Compound']]}{currentStint['Compound']}"
			else:
				currentCompound = currentStint['Compound']
			
			# Get personal best lap time 
			if type( self.timingDataF1["Lines"][RacingNumber]["BestLapTime"] ) == dict:
				# Not qualifying
				BestLapTime = self.timingDataF1["Lines"][RacingNumber]["BestLapTime"]["Value"]
			elif type( self.timingDataF1["Lines"][RacingNumber]["BestLapTime"] ) == list:
				# qualifying
				BestLapTime = self.timingDataF1["Lines"][RacingNumber]["BestLapTime"][self.timingDataF1["SessionPart"] - 1]["Value"]
			
			# skip if time is empty
			if BestLapTime == "":
				continue
			
			if (
				"OverallFastest" in stat["LastLapTime"]
				and stat["LastLapTime"]["OverallFastest"] == True
			):
				# Quickest Overall
				self.discord.post(
					username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
					embeds=[
						{
							"title": f"Quickest Overall - {BestLapTime}",
							"fields": [
								{
									"name": "Sectors",
									"value": "".join([
										"\U0001F7EA" if sector["OverallFastest"] else # purple square emoji
										"\U0001F7E9" if sector["PersonalFastest"] else # green square emoji
										"\U0001F7E8" # yellow square emoji
										for sector in self.timingDataF1["Lines"][RacingNumber]["Sectors"]
									]),
									"inline": True
								},
								{
									"name": "Tyre",
									"value": f"{currentCompound} (age: {currentStint['TotalLaps']})",
									"inline": True
								},
							],
							"color": 10181046 #Purple
						}
					],
					avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
				)
			elif (
				self.sessionInfo["Type"] in ["Qualifying", "Sprint Shootout"]
			):
				# Personal Best
				self.discord.post(
					username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
					embeds=[
						{
							"title": f"Personal Best - {BestLapTime}",
							"fields": [
								{
									"name": "Sectors",
									"value": "".join([
										"\U0001F7EA" if sector["OverallFastest"] else
										"\U0001F7E9" if sector["PersonalFastest"] else
										"\U0001F7E8"
										for sector in self.timingDataF1["Lines"][RacingNumber]["Sectors"]
									]),
									"inline": True
								},
								{
									"name": "Tyre",
									"value": f"{currentCompound} (age: {currentStint['TotalLaps']})",
									"inline": True
								},
							],
							"color": 5763719 #Green
						}
					],
					avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
				)
		
		# Knocked Out of Qualifying
		if (
			self.sessionInfo["Type"] in ["Qualifying", "Sprint Shootout"] and
			"KnockedOut" in stat and 
			stat["KnockedOut"] == True
		):
			self.discord.post(
				username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
				embeds=[
					{
						"title": f"Knocked Out - P{self.timingDataF1['Lines'][RacingNumber]['Position']}",
						"color": int(info['TeamColour'], 16),
					}
				],
				avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
			)
		
		# Retired
		if (
			"Retired" in stat and 
			stat["Retired"] == True
		):
			self.discord.post(
				username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
				embeds=[
					{
						# "title": f"Retired - Lap {self.timingDataF1['Lines'][RacingNumber]['NumberOfLaps'] + 1}",
						"title": f"Retired{ (' - Lap ' + str(self.timingDataF1['Lines'][RacingNumber]['NumberOfLaps'] + 1) )if 'NumberOfLaps' in self.timingDataF1['Lines'][RacingNumber] else '' }",
						"color": int(info['TeamColour'], 16),
					}
				],
				avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
			)
		
		# Race Leader
		if (
			self.sessionInfo["Type"] in ["Race", "Sprint"] and
			"Position" in stat and 
			stat["Position"] == "1"
		):
			self.discord.post(
				username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
				embeds=[
					{
						"title": f"Race Leader - {info['FullName']}",
						"fields": [
							{"name": "TeamName", "value": info["TeamName"], "inline": True},
						],
						"color": int(info['TeamColour'], 16),
					}
				],
				avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
			)
		
	return