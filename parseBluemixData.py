import pandas
import ipdb

########
#
#	WIP, do not use yet!
#
########
datafile = "data/raw_bluemix_analysis.csv"
commentsfile = "data/mergedData.csv"

data1 = pandas.read_csv(datafile, sep = ";")
data2 = pandas.DataFrame(columns=('comment', 'anger', 'disgust', 'fear', 'joy', 'sadness', 'analytical', 'confident', 'tentative', 'openness', 'conscientiousness', 'extraversion', 'agreableness', 'emotionalrange'))

for i,entry in data1["tone_analysis"].iteritems():
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

	data2.loc[i] = [comment, anger, disgust, fear, joy, sadness, analytical, confident, tentative, openness, conscientiousness, extraversion, agreableness, emotionalrange]

comments = pandas.open_csv(commentsfile, sep=";")

finaldataset = pandas.merge(comments, data2, on="gh_issue_comments", how="outer")