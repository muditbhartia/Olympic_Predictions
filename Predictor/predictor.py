from json import dumps
import sys

def readFromFile(filename):
	data = []
	with open(filename, 'r') as file:
		columns = file.readline().rstrip()
		columns = columns.split('\t')

		for row in file:
			row = row.rstrip().split('\t')
			i = 0
			temprow = {}
			for column in columns:
				temprow[column] = row[i]
				i = i+1
			data.append(temprow)
	return data


def writeToFile(filename, data):
	writeString = ''
	columns = []

	for column in data[0].keys():
		columns.append(column)
		writeString = writeString + column + '\t'
	writeString = writeString + '\n'

	for entry in data:
		for column in columns:
			writeString = writeString + entry[column] + '\t'
		writeString = writeString + '\n'
	
	with open(filename, 'w') as file:
		file.write(writeString)
	return


def jsonWriteToFile(filename, data):
	with open(filename, 'w') as file:
		file.write(dumps(data))
	return


def cleanCCRegion(cc_regions):
	cleaned = {}
	for entry in cc_regions:
		cleaned[entry['Country Code']] = entry['Region']
	return cleaned


def countMedals(dataset, cc_regions):
	medal_count = {}
	for entry in dataset:
		year = entry['Edition']
		region = cc_regions[entry['NOC']]

		if year in medal_count:
			currentYear = medal_count[year]
		else:
			currentYear = {'total': 0}
		
		if region in currentYear:
			count = currentYear[region]
		else:
			count = 0

		currentYear['total'] = currentYear['total'] + 1
		currentYear[region] = count + 1
		medal_count[year] = currentYear
	return medal_count


def calculateRatio(medal_count):
	ratio = {}
	for year in medal_count:
		tempyear = {}
		for region in medal_count[year]:
			if region != 'total':
				tempyear[region] = medal_count[year][region]/medal_count[year]['total']
		ratio[year] = tempyear
	return ratio


def rearrangeRatio(ratio):
	regionData = {}
	for year in ratio:
		for region in ratio[year]:
			if region in regionData:
				tempRegion = regionData[region]
			else:
				tempRegion = {}

			tempRegion[year] = ratio[year][region]
			regionData[region] = tempRegion
	return regionData


def determineAverage(regionData):
	averages = {}
	total = 0.0
	for region in regionData:
		ratio_sum = 0.0
		for year in regionData[region]:
			ratio_sum = ratio_sum + regionData[region][year]
		averages[region] = ratio_sum/len(regionData[region])
		total = total + averages[region]
	
	averages['total'] = total
	return averages


def normalize(averages):
	prediction = {}
	for region in averages:
		if region != 'total':
			prediction[region] = averages[region]/averages['total']
	return prediction


def prepareForFile(data):
	prepped = []
	for year in data:
		for region in data[year]:
			temp = {'Year': str(year), 'Region': region, 'Ratio': str(data[year][region])}
			prepped.append(temp)

	return prepped


def verboseCCRegion(cc_regions):
	print("\nCountry Codes - Regions\n")
	for cc in cc_regions:
		print(cc + ": " + cc_regions[cc])
	print("\n")


def verboseMedalCount(medal_count):
	print("\nMedal Count by Region per Year\n")
	for year in medal_count:
		print(year, ":")
		for region in medal_count[year]:
			if region !='total':
				print("\t", region, "\t", medal_count[year][region])
		print("\t", "Total", "\t", medal_count[year]['total'], "\n")
	print("\n")


def verboseRatio(ratio):
	print("\nPercentage of Medals won by Region per Year\n")
	for year in ratio:
		print(year, ":")
		total = 0.0
		for region in ratio[year]:
			total = total + float(ratio[year][region]*100)
			print("\t", region, "\t", float(ratio[year][region])*100)
		print()
	print("\n")


def verboseRegionData(regionData):
	print("\nPercentage of Medals won by Year per Region\n")
	for region in regionData:
		print(region, ":")
		for year in regionData[region]:
			print("\t", year, "\t", float(regionData[region][year])*100)
		print()
	print("\n")
	return


def verboseAverages(averages):
	print("\nAverage of all Ratios by Region\n")
	for region in averages:
		print(region, "\t", float(averages[region])*100)
	print("\n\n")
	return


def verbosePrediction(prediction):
	print("\nPrediction of Distribution of Medals for the Next Edition\n")
	for region in prediction:
		print(region, "\t", float(prediction[region])*100)
	print("\n\n")
	return


def generateData(dataset, cycles):
	verbose = True if len(sys.argv)==2 and sys.argv[1] == '-v' else False

	cc_regions = cleanCCRegion(readFromFile('cc-region.txt'))
	if verbose:
		verboseCCRegion(cc_regions)

	medal_count = countMedals(dataset, cc_regions)
	if verbose:
		verboseMedalCount(medal_count)

	ratio = calculateRatio(medal_count)
	if verbose:
		verboseRatio(ratio)

	for i in range(cycles):
		regionData = rearrangeRatio(ratio)
		if verbose:
			verboseRegionData(regionData)

		averages = determineAverage(regionData)
		if verbose:
			verboseAverages(averages)

		prediction = normalize(averages)
		if verbose:
			verbosePrediction(prediction)

		latestYear = max(ratio.keys())

		verboseRatio({str(int(latestYear)+4): prediction})
		ratio[str(int(latestYear)+4)] = prediction

	data = prepareForFile(ratio)
	return data


dataset = readFromFile('dataset.txt')
cycles = int(input("How many editions do you want to predict ahead?\n>"))

new_dataset = generateData(dataset, cycles)
writeToFile('output.txt', new_dataset)
