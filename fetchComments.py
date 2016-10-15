# This script is used to extract comments on pull requests from Github.
# It gets everything and writes it to the specified file

import ipdb
import ConfigParser
import ghhelper
import json
import pandas
import time
from pprint import pprint

#initial files
configFile = "./keysconfig.txt"
travisData = "travistorrent_30_9_2016.csv"

# Output
outputfile = "./data/comments.csv"

def get_from_config(section, config_tags):
	# Reads the configFile file and returns the config tags located in specified section.
	config = ConfigParser.ConfigParser()
	config.read(configFile)
	if isinstance(config_tags,list):
		config_data = {k: config.get(section, k) for k in config_tags}
	else:
		config_data = {config_tags: config.get(section, config_tags)}
	return config_data

def load_travis_data():
	# Loads and filter the travis dataset.
	travisFields = 	[
			"tr_build_number", 
			"tr_status", 
			"tr_tests_ran",
			"tr_tests_failed", 
			"gh_project_name", 
			"gh_lang",
			"gh_team_size",
			"git_num_committers",
			"gh_sloc",
			"git_commit", 
			"git_num_commits",
			"git_commits",
			"gh_by_core_team_member",
			"gh_is_pr", 
			"gh_pull_req_num", 
			"gh_description_complexity",
			"gh_num_commit_comments", 
			"gh_num_pr_comments", 
			"gh_num_issue_comments"
			]

	df = pandas.read_csv(travisData)
	return df[travisFields]


def find_build_job(data, commitId):
	
	buildJob = data[data.git_commit == commitId]

	if buildJob.empty:
	 	sub = data.git_commits
		#ipdb.set_trace()	 	
	 	for label, commitStr in sub.iteritems():
			commits = commitStr.split('#')
			b = next((c for c in commits if c==commitId), None)
			if b != None:
				#ipdb.set_trace()
				buildJob = data.loc[label]				
				break
	else:
		buildJob=buildJob.iloc[0]

	return buildJob



if __name__ == "__main__":

	# Init github client
	creds = get_from_config("gh_client",["username","oauth_token"])
	ghc = ghhelper.GithubClient(credentials=creds, ignoring_errors=True)

	print "Loading Travis data..."
	td = load_travis_data()

	projectNames = td["gh_project_name"]
	projectNames = projectNames.drop_duplicates()

	# garg = find_build_job(td, "20403b8040e70ba23de28446efd22fb5a82a481b")
	# garg = find_build_job(td, "6f88fd4fb3ca219337e75e16f22dcd88ad7ee7d1")

	#dfColumns = list(td.columns.values)
	dfColumns = list()
	headers = [
		"job_commit",
		"comment_commit",
		"gh_comment_id",
		"gh_comment_type",
		"gh_created_at",
		"gh_updated_at",
		"gh_user_id",
		"gh_user_login",
		"gh_body",
		"gh_reactions"
	]
	dfColumns.extend(headers)
 	outData = pandas.DataFrame(columns=dfColumns)

	
	response = ghc.check_rate_limit()
	limit=0
	remaining=0
	resetTime=0
	#ipdb.set_trace()
	if response != None and response.status_code == 200:
		limit = response.json()["rate"]["limit"]
		remaining = response.json()["rate"]["remaining"]
		resetTime = response.json()["rate"]["reset"]
		print "GitHub api request limit info:\nlimit : %s\nremaining : %s\nreset : %s\n"%(limit, remaining, resetTime)

  	# We fetch the raw json comment data
  	print "Fetching comments..."
  	jsonData = []
  	index=0
  	nbRequests = 0
  	for label, prj in projectNames.iteritems():
  		print "Progress : %s/%s : comments for %s"%(index,len(projectNames),prj)

  		prjData = td[td.gh_project_name == prj]

  		prjJson = {prj : {"repo" : [], "issue" : [], "pull_r" : []}}

  		# We retrieve all comments for the project.
  		# TODO : fix encoding? Currently unicode since there are emojis...
  		try:
			response = ghc.get_repo_comments(prj)
			nbRequests = nbRequests+1
			if response != None and response.status_code == 200:
				prjJson[prj]["repo"] = response.json()		

			response = ghc.get_pull_request_comments(prj)
			nbRequests = nbRequests+1
			if response != None and response.status_code == 200:
				prjJson[prj]["pull_r"] = response.json()

			response = ghc.get_issue_comments(prj)
			nbRequests = nbRequests+1
			if response != None and response.status_code == 200:
				prjJson[prj]["issue"] = response.json()

		except:
			ipdb.set_trace()

		if nbRequests >= limit:
			waitTime = resetTime - time.time() + 10
			print "GitHub api request limit reached. The limit will be reset in %s seconds"%(waitTime)
			while waitTime > 0:
				sleep(10*60)
				waitTime = waitTime - 10*60
				print "%s seconds remaining..."%(waitTime)
				
		jsonData.append(prjJson)
		index = index+1

	try:
		with open('./data/comments.json', 'w') as outfile:
	    		json.dump(jsonData, outfile)
	except:
		ipdb.set_trace()
	