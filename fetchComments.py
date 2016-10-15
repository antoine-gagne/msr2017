# This script is used to fetch comments on several projects from Github.
# It gets all 3 types of comments (commits, issues and pull requests) and writes 
# the raw JSOn data to a file

import ipdb
import ConfigParser
import ghhelper
import json
import pandas
import time
import sys
from pprint import pprint

#initial files
configFile = "./keysconfig.txt"
travisData = "travistorrent_30_9_2016.csv"

# Output
outputfile = "./data/comments.json"

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
	# Finds the corresponding build job in the Travis dataset associated with the specified commit id.
	
	# We first check in the "git_commit" column
	buildJob = data[data.git_commit == commitId]

	if buildJob.empty:
		# If not found, it may be in the "git_commits" (with an 's') column
	 	sub = data.git_commits
	 	for label, commitStr in sub.iteritems():
			commits = commitStr.split('#')
			job = next((c for c in commits if c==commitId), None)
			if job != None:
				buildJob = data.loc[label]				
				break
	else:
		buildJob=buildJob.iloc[0]

	return buildJob


def dump_json(data, filename):
	try:
		with open(filename, 'w') as outfile:
	    		json.dump(jsonData, outfile)
	except:
		ipdb.set_trace()


if __name__ == "__main__":

	# Init github client
	creds = get_from_config("gh_client",["username","oauth_token"])
	ghc = ghhelper.GithubClient(credentials=creds, ignoring_errors=True)

	print "Loading Travis data..."
	td = load_travis_data()

	projectNames = td["gh_project_name"]
	projectNames = projectNames.drop_duplicates()

	# We first get the api requests limit
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
  	nbJsonFiles = 0
  	for label, prj in projectNames.iteritems():
  		print "Progress : %s/%s : fetching comments for %s"%(index,len(projectNames),prj)

  		prjData = td[td.gh_project_name == prj]

  		prjJson = {prj : {"repo" : [], "issue" : [], "pull_r" : []}}

  		# We retrieve all comments for the project.
  		try:
  			# TODO : fix encoding? Currently unicode since there are emojis...
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

		# We wait the specified amount of time if the api request limit is reached
		if nbRequests >= limit:
			waitTime = resetTime - time.time() + 10
			print "GitHub api request limit reached. The limit will be reset in %s seconds"%(waitTime)
			while waitTime > 0:
				sleep(10*60)
				waitTime = waitTime - 10*60
				print "%s seconds remaining..."%(waitTime)
				
		jsonData.append(prjJson)

		size = sys.getsizeof(jsonData)
		# Dump JSON data in a file. We creates ~10MB files
		if size > 10*1024*1024:
			dump_json(jsonData, ".data/comments%s.json"%nbJsonFiles)
			nbJsonFiles = nbJsonFiles+1
			jsonData = []

		index = index+1

	# Last dump
	dump_json(jsonData, "comments%s.json"%nbJsonFiles)
	