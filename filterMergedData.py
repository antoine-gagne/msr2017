# Filter from merged data to reduce the number of calls to bluemix API tu under 1000

import pandas
import ipdb
import json
import time
import bluemixhelper
import ConfigParser

configFile = "./keysconfig.txt"
outFile = "data/raw_bluemix_analysis.csv"
filename = "data/mergedData.csv" # the filtered one

def get_from_config(section, config_tags):
	# Reads the configFile file and returns the config tags located in specified section.
	config = ConfigParser.ConfigParser()
	config.read(configFile)
	if isinstance(config_tags,list):
		config_data = {k: config.get(section, k) for k in config_tags}
	else:
		config_data = {config_tags: config.get(section, config_tags)}
	return config_data


def filter_merged_data(df):

	# First, only take pull requests. Because.
	sub = df[df["gh_is_pr"] == True]
	# 49803 rows

	# We then drop lines where there are no comments on the pull request
	sub = sub.dropna(subset=["gh_issue_comments"])

	# Keep only rubies. Because.
	sub = sub[sub['gh_lang']=='ruby']

	return sub

def unique_filtered_data(data_in):
	# GROUPBY on gh_pr_comments field, so that multiple builds corresponding to the same comment chains are analyzed only once
	data_out = data_in[["gh_issue_comments"]]
	data_out = data_out.drop_duplicates()
	return data_out
	###
	## The reason this removes so many results is that some pull requests had had many updates, and the comment thread appears many times in there. this demonstrate it:
	## sub = sub.groupby(["gh_issue_comments"]).agg(['count'])
	###

if __name__ == "__main__":

	df = pandas.read_csv(filename, sep = ";")
	data = filter_merged_data(df)
	data2 = unique_filtered_data(data)
	
	creds = get_from_config("bluemix_client",["username","password"])
	bmc = bluemixhelper.BluemixClient(credentials=creds, verbose=True)


	tone_analysis = pandas.DataFrame(columns=('issue_comment', 'tone_analysis'))


	# data_string_test = data2["gh_issue_comments"][41]


	ipdb.set_trace()
	try:
		progress = 0
		for i, comment in data2["gh_issue_comments"].iteritems():
			print "%s / %s " %(progress, len( data2["gh_issue_comments"]))
			try:
				analysis = bmc.get_tone_analysis(comment)
				tone_analysis.loc[i] = [comment, json.loads(analysis.content)]
			except:
				print "Caught error"
				tone_analysis.loc[i] = [comment, ""]
			time.sleep(0.5)

			tone_analysis.to_csv(outFile, sep=';', encoding='utf-8') # TODO MOVE OUT OF HERE
			progress += 1
	except:
		ipdb.set_trace()
	print "complete!"