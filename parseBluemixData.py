import pandas
import ipdb
import json
import filterMergedData

########
#
#	WIP, do not use yet!
#
########

def repair_string_for_json(string):
	index = string.find("'sentences_tone'")
	if index != -1:
		cropped_string = string[:index]
		cropped_string = cropped_string.replace("u'","'").replace("'",'"')
		try:
			return json.loads(cropped_string[:-3]+"}")
		except:
			ipdb.set_trace()
	else:
		print "return empty"
		return {}

datafile = "data/raw_bluemix_analysis.csv"
commentsfile = "data/mergedData.csv"
data1 = pandas.read_csv(datafile, sep = ";")
empty_value = 0

data2 = pandas.DataFrame(columns=('comment', 'anger', 'disgust', 'fear', 'joy', 'sadness', 'analytical', 'confident', 'tentative', 'openness', 'conscientiousness', 'extraversion', 'agreableness', 'emotionalrange'))
ipdb.set_trace()

for i,entry in data1["tone_analysis"].iteritems():

	entry = repair_string_for_json(entry)

	if entry:
		# emotion tone
		anger = entry["document_tone"]['tone_categories'][0]['tones'][0]['score']
		disgust = entry["document_tone"]['tone_categories'][0]['tones'][1]['score']
		fear = entry["document_tone"]['tone_categories'][0]['tones'][2]['score']
		joy = entry["document_tone"]['tone_categories'][0]['tones'][3]['score']
		sadness = entry["document_tone"]['tone_categories'][0]['tones'][4]['score']
		# language tone
		analytical = entry["document_tone"]['tone_categories'][1]['tones'][0]['score']
		confident = entry["document_tone"]['tone_categories'][1]['tones'][1]['score']
		tentative = entry["document_tone"]['tone_categories'][1]['tones'][2]['score']
		# social tone
		openness = entry["document_tone"]['tone_categories'][2]['tones'][0]['score']
		conscientiousness = entry["document_tone"]['tone_categories'][2]['tones'][1]['score']
		extraversion = entry["document_tone"]['tone_categories'][2]['tones'][2]['score']
		agreableness = entry["document_tone"]['tone_categories'][2]['tones'][3]['score']
		emotionalrange = entry["document_tone"]['tone_categories'][2]['tones'][4]['score']

		data2.loc[i] = [data1["issue_comment"][i], anger, disgust, fear, joy, sadness, analytical, confident, tentative, openness, conscientiousness, extraversion, agreableness, emotionalrange]
	else:
		data2.loc[i] = [data1["issue_comment"][i], empty_value, empty_value, empty_value, empty_value, empty_value, empty_value, empty_value, empty_value, empty_value, empty_value, empty_value, empty_value, empty_value]

comments = pandas.read_csv(commentsfile, sep=";")

#filter comments as they were in filterMergedData, but without the unique constraint
comments = filterMergedData.filter_merged_data(comments)

finaldataset = pandas.merge(comments, data2, left_on="gh_issue_comments",right_on="comment", how="left")