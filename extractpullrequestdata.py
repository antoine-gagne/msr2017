# This script is used to extract comments on pull requests from Github.
# It gets everything and writes it to the specified file

import ipdb
import ConfigParser
import ghhelper
import json
import pandas

#initial files
configFile = "./keysconfig.txt"
travisData = "./travistorrent-5-3-2016.csv"

# Output
outputfile = "./pullreqdata.txt"


def get_from_config(section, config_tags):
	# Reads the configFile file and returns the config tags located in specified section.
	config = ConfigParser.ConfigParser()
	config.read(configFile)
	if isinstance(config_tags,list):
		config_data = {k: config.get(section, k) for k in config_tags}
	else:
		config_data = {config_tags: config.get(section, config_tags)}
	return config_data

def load_travis_data(columns):
	# Provide columns [c1, c2, ...]
	df = pd.read_csv(travisData, usecols=fields)


if __name__ == "__main__":

	# Extract builds which were pull requests, and get pull request ID
	travisFields = ["gh_project_name", "gh_is_pr", "gh_pull_req_num", "gh_num_pr_comments"]
	df = pandas.read_csv(travisData)
	sub = df[travisFields] 
	sub = sub[sub["gh_is_pr"] == True]
	sub = sub.drop_duplicates(subset=["gh_project_name","gh_pull_req_num"])

	# This yields 58099 rows out of 2640825, which is still a lot. Filter to only get the pull requests with more than 5 comments. There are 914, which is much more manageable, and will be much more efficient to analyze with Bluemix.
	sub = sub[sub["gh_num_pr_comments"]>5]
 	data = pandas.DataFrame(columns=('gh_project_name', 'gh_pull_req_num', 'gh_pr_comments'))
 	i=0
 	ipdb.set_trace()
	for index, row in sub.iterrows():
		data.loc[i] = [row["gh_project_name"], row["gh_pull_req_num"], "test"]
		i=i+1
	ipdb.set_trace()


	"""
	creds = get_from_config("gh_client",["client_id","client_secret"])
	ghc = ghhelper.GithubClient(creds, verbose=True)
	data = ghc.get_single_pull_request("zxing/zxing",677)

	with open(outputfile, 'w') as outfile:
	    json.dump(data.json(), outfile)
	"""