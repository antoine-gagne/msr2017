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

def find_build_job_by_commit(data, commitId):
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


if __name__ == "__main__":

	# Init github client
	creds = get_from_config("gh_client",["username","oauth_token"])
	ghc = ghhelper.GithubClient(credentials=creds, ignoring_errors=True)

	print "Loading Travis data..."
	td = load_travis_data()

	projectNames = td["gh_project_name"]
	projectNames = projectNames.drop_duplicates()


	#dfColumns = list(td.columns.values)
	dfColumns = list()
	headers = [
		"job_commit",
		"comment_commit",
		"gh_pull_req_num",
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
	# headers = [
	# 	"gh_body"
	# ]
	# dfColumns.append(headers)
 	outData = pandas.DataFrame(columns=dfColumns)

	# We first get the api requests limit
	response = ghc.check_rate_limit()
	limit=0
	remaining=0
	resetTime=0
	if response != None and response.status_code == 200:
		limit = response.json()["rate"]["limit"]
		remaining = response.json()["rate"]["remaining"]
		resetTime = response.json()["rate"]["reset"]
		print "GitHub api request limit info:\nlimit : %s\nremaining : %s\nreset : %s\n"%(limit, remaining, resetTime)

	#ipdb.set_trace()

  	# We fetch the raw json comment data
  	print "Fetching comments..."
  	index=0


  	#DEBUG
  	#======
  	projectNames = td[td["gh_project_name"] == "Albacore/albacore"]
  	projectNames = projectNames["gh_project_name"]
  	projectNames = projectNames.drop_duplicates()
  	#ipdb.set_trace()
	#======


  	for label, prj in projectNames.iteritems():
  		print "Progress : %s/%s : fetching comments for %s"%(index,len(projectNames),prj)

  		prjData = td[td.gh_project_name == prj]
  		
  		# We first get all repo comments
		response = ghc.get_repo_comments(prj)
		if response != None and response.status_code == 200:
			repoComments = response.json()		
			for commentData in repoComments:
				commitId = commentData["commit_id"]

				# We try to find an associated commit id in the Travis dataset
				job = find_build_job_by_commit(prjData, commitId)
				if not job.empty:
					data = [
						job.git_commit,
						commitId,
						-1,
						commentData["id"],
						"repo",
						commentData["created_at"],
						commentData["updated_at"],
						commentData["user"]["id"],
						commentData["user"]["login"],
						commentData["body"],
						""
					]
					outData.loc[len(outData)] = data;



		#=====================
		# NOT ALL PULL REQUESTS ARE RETURNED... WHY?!
		# Need to investigate
		#=====================

		# For the other comments, we need to get all pull requests first			
		response = ghc.get_pull_request_for_repo(prj)
		if response == None or response.status_code != 200:
			continue

		pullRequests = response.json()

		# We also get all pull request comments and issue comments right now to reduce 
		# the number of requests made to the Github api
		pullRequestComments = []
		response = ghc.get_pull_request_comments(prj)
		if response != None and response.status_code == 200:
			pullRequestComments = response.json()

		issueComments = []
		response = ghc.get_issue_comments(prj)
		if response != None and response.status_code == 200:
			issueComments = response.json()

		# We search in the Travis dataset a build job corresponding to the pull request number	
		for pullrData in pullRequests:
			
			jobs = prjData[prjData["gh_pull_req_num"] == pullrData["number"]]

			ipdb.set_trace()
			
			for job in jobs:
				
				ipdb.set_trace()

				# We search the matching pull request number in the pull request comments
				for prComment in pullRequestComments:
					if prComment.pull_request_url == pullrData.url:
						data = [
							job.git_commit,
							prComment["commit_id"],
							job.gh_pull_req_num,
							prComment["id"],
							"pull_r",
							prComment["created_at"],
							prComment["updated_at"],
							prComment["user"]["id"],
							prComment["user"]["login"],
							prComment["body"],
							""
						]
						outData.loc[len(outData)] = data;

				# We do the same thing for issue comments
				for issueComment in issueComments:
					if issueComment.html_url.find(pullrData.number) !=-1:
						data = [
							job.git_commit,
							"",
							job.gh_pull_req_num,
							issueComment["id"],
							"issue",
							issueComment["created_at"],
							issueComment["updated_at"],
							issueComment["user"]["id"],
							issueComment["user"]["login"],
							issueComment["body"],
							""
						]
						outData.loc[len(outData)] = data;


		# We wait the specified amount of time if the api request limit is reached
		if ghc.nbRequestsMade >= limit:
			waitTime = resetTime - time.time() + 10
			print "GitHub api request limit reached. The limit will be reset in %s seconds"%(waitTime)
			while waitTime > 0:
				print "%s seconds remaining..."%(waitTime)
				sleep(min(10*60, waitTime))
				waitTime = waitTime - 10*60
		index=index+1


	# We write the data to a csv file
	try:
		outData.to_csv(outputfile)
	except:
		ipdb.set_trace()


	