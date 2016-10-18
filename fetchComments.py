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

# Output
outputDir = util.commentsDir

if __name__ == "__main__":

	# Init github client
	creds = get_from_config(util.configFile, "gh_client",["username","oauth_token"])
	ghc = ghhelper.GithubClient(credentials=creds, ignoring_errors=True)
	util = util.Util(ghc)

	print "Loading Travis data..."
	td = util.load_travis_data(util.filteredTravisData)

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