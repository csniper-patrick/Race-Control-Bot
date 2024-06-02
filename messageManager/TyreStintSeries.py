import copy
from .utils import *

def liveTyreStintSeriesHandler(self, msg):
	compoundColor=self.msgStyle["compoundColor"]
	compoundSymbol=self.msgStyle["compoundSymbol"]
	prevFrame = copy.deepcopy(self.tyreStintSeries)
	self.tyreStintSeries = updateDictDelta(self.tyreStintSeries, msg["A"][1])
	if self.sessionInfo["Type"] not in ["Race", "Sprint"]:
		return
	for RacingNumber, driverStints in self.tyreStintSeries["Stints"].items():
		if ( RacingNumber not in self.driverList or len(driverStints) == 0 ):
			continue
		info = self.driverList[RacingNumber]
		currentStint = driverStints[-1]
		if currentStint['Compound'] in compoundSymbol:
			currentCompound = f"{compoundSymbol[currentStint['Compound']]}{currentStint['Compound']}"
		else:
			currentCompound = currentStint['Compound']
		# announce tyre change if necessary
		if ( len(driverStints) > len(prevFrame['Stints'][RacingNumber]) ):
			# case 1 new stints
			self.discord.post(
				username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
				embeds=[
					{
						"title": f"Tyre Change - { currentCompound }",
						"fields": [
							{"name": "Stint", "value": len(driverStints), "inline": True},
							{"name": "Age", "value": currentStint["StartLaps"], "inline": True},
						],
						"color": compoundColor[currentStint["Compound"]] if "Compound" in currentStint and currentStint["Compound"] in compoundColor else None,
					}
				],
				avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
			)
		elif( len(driverStints) == len(prevFrame['Stints'][RacingNumber]) and currentStint['Compound'] != prevFrame['Stints'][RacingNumber][-1]['Compound'] ):
			# case 2 compound update
			self.discord.post(
				username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
				embeds=[
					{
						"title": f"Compound - { currentCompound } (Updated)",
						"fields": [
							{"name": "Stint", "value": len(driverStints), "inline": True},
							{"name": "Age", "value": currentStint["StartLaps"], "inline": True},
						],
						"color": compoundColor[currentStint["Compound"]] if "Compound" in currentStint and currentStint["Compound"] in compoundColor else None,
					}
				],
				avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
			)
	return