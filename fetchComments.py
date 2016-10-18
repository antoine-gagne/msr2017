# This script is used to fetch comments on several projects from Github.
# It gets all 3 types of comments (commits, issues and pull requests) and writes 
# the raw JSOn data to a file

import ipdb
import ConfigParser
import ghhelper
import util
import json
import pandas
import sys
import os
import datetime
import time
import signal
from pprint import pprint

#initial files
configFile = "./keysconfig.txt"
travisData = "travistorrent_30_9_2016.csv"
filteredTravisData = "./data/filteredTravisData.csv"

# Output
outputDir = "./data/comments/"

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
	# TODO : Investigate why there are duplicates... 
	# This could indicates that they did not parsed their data correctly
	travisFields = 	[
			"row",
			"tr_build_id",
			"tr_build_number", 
			"tr_num_jobs",
			"tr_jobs",
			"tr_job_id",
			"tr_status",
			"tr_duration",
			"tr_started_at", 
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

	df = pandas.read_csv(filteredTravisData)
	data = df[travisFields]
	
	#DEBUG
	#==================
	# Creating subset of travis data where : 
	# Team size >= 10 and nb line of codes >= 10000
	# == 135 projects
	#sub = data[ (data["gh_team_size"] >= 10) & (data["gh_sloc"] >= 10000) ]
	#sub.to_csv("./data/filteredTravisData.csv", encoding='utf-8', index=False)
	#ipdb.set_trace()
	#==================
	return data.drop_duplicates(subset=travisFields)

if __name__ == "__main__":

	# Init github client
	creds = get_from_config("gh_client",["username","oauth_token"])
	ghc = ghhelper.GithubClient(credentials=creds, ignoring_errors=True)
	util = util.Util(ghc)

	print "Loading Travis data..."
	td = load_travis_data()

	projectNames = td["gh_project_name"]
	projectNames = projectNames.drop_duplicates()
	projectNames = projectNames.sort_values()

	startTime = time.time()
  	print "Fetching comments..."
  	index=0
  	for label, prj in projectNames.iteritems():

		dir = "%s%s/"%(outputDir, prj)
		if not os.path.exists(dir):
				os.makedirs(dir)

  		print "Progress : %s/%s : fetching comments for %s"%(index,len(projectNames),prj)

  		# We first get all repo comments
		commentFile = "%s%s.json"%(dir, util.repoStr)
		if os.path.isfile(commentFile):
			print "\tSkipping repo comments. Already fetched."
		else:
			repoComments = util.fetch_comments(util.repoStr, prj)
			print "\t%s repo comments found"%(len(repoComments))
			if repoComments:			
				with open(commentFile, 'w') as outfile:
    					json.dump(repoComments, outfile)

		# We then get all pull request comments
		commentFile = "%s%s.json"%(dir, util.prStr)
		if os.path.isfile(commentFile):
			print "\tSkipping pull request comments. Already fetched."
		else:
			pullRequestComments = util.fetch_comments(util.prStr, prj)
			print "\t%s pull request comments found"%(len(pullRequestComments))
			if pullRequestComments:
					with open(commentFile, 'w') as outfile:
	    					json.dump(pullRequestComments, outfile)	

		# Finally, we retrieve issue comments
		commentFile = "%s%s.json"%(dir, util.issueStr)
		if os.path.isfile(commentFile):
			print "\tSkipping issue comments. Already fetched."
		else:
			issueComments = util.fetch_comments(util.issueStr, prj)
			print "\t%s issue comments found"%(len(issueComments))
			if issueComments:
					with open(commentFile, 'w') as outfile:
	    					json.dump(issueComments, outfile)
				
		index = index+1

	print "Fetching completed!"
	print "Duration : %s"%(str(datetime.timedelta(seconds=time.time()-startTime)))