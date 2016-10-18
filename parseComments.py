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

#commentsDir = util.commentsDir
commentsDir = "./data/comments-test/"

partialOutputfile = "./data/comments_partial.csv"

def build_comment_data(cData, commitId, reactions=""):
	#ipdb.set_trace()
	data = {
		"commit_found" : commitId,
		"gh_comment_id" : cData["id"],
		"gh_user_id" : cData["user"]["id"] if cData["user"] else None,
		"gh_user_login" : cData["user"]["login"] if cData["user"] else None,
		"gh_created_at" : cData["created_at"],
		"gh_updated_at" : cData["updated_at"],
		"gh_body" : cData["body"],
		"gh_reactions" : reactions
		}
	return data;

def load_comments(commentsType, project):
	path = "%s%s/%s.json"%(commentsDir, project, commentsType)
	with open(path) as jsonFile:    
    		return = json.load(jsonFile)


def signal_handler(signum, frame):
    raise KeyboardInterrupt, "Signal handler"

if __name__ == "__main__":

	# handle Ctrl+C
	signal.signal(signal.SIGINT, signal_handler)

	# Init github client
	creds = get_from_config(util.configFile, "gh_client",["username","oauth_token"])
	ghc = ghhelper.GithubClient(credentials=creds, ignoring_errors=True)
	util = util.Util(ghc)

	print "Loading Travis data..."
	td = util.load_travis_data(util.filteredTravisData)

	projectNames = td["gh_project_name"]
	projectNames = projectNames.drop_duplicates()
	projectNames = projectNames.sort_values()

	# We check if there is already a file partially created from a previous run
	outData	= {}
	# fromPartialFile = os.path.isfile(partialOutputfile)
	# if fromPartialFile:
	# 	print "Partial file from a previous job found. Loading it..."
	# 	with open(partialOutputfile) as jsonFile:    
 #    			outData = json.load(jsonFile)
	#======

	currentPrj =""
	completed=False
	startTime = time.time()
	try:
	  	print "Parsing comments..."
	  	index=0
	  	for label, prj in projectNames.iteritems():

	  	# 	if prj in outData:
	  	# 		# We already fetched this project's comments during a previous run.
				# print "Progress : %s/%s : Skipping %s. Data already fetched."%(index,len(projectNames),prj)	  			
				# index = index+1
				# continue
			#if index==2:raise Exception('test')

			outData[prj] = {}

	  		print "Progress : %s/%s : parsing comments for %s"%(index,len(projectNames),prj)
	  		currentPrj = prj	
	  		prjData = td[td.gh_project_name == prj]

	  		# We first get all repo comments
	  		nbMatched=0
			repoComments = load_comments(util.repoStr, prj)
			print "\t%s repo comments found"%(len(repoComments)),
			if repoComments:
				outData[prj][util.repoStr] = {}
				for repoComment in repoComments:
					commitId = repoComment["commit_id"]

					# We try to find an associated commit id in the Travis dataset
					jobs = util.find_build_jobs_by_commit(prjData, commitId)
					if not jobs.empty:
						repoC = outData[prj][util.repoStr]
						for label, job in jobs.iterrows():
							travis_data_row = int(job.row)
							if travis_data_row not in repoC:
								repoC[travis_data_row] = []
							repoC[travis_data_row].append(build_comment_data(repoComment, commitId));

						nbMatched=nbMatched+1
				print "\t%s matched"%(nbMatched),
			print ""

			# We then get all pull request comments
			nbMatched=0
			pullRequestComments = load_comments(util.prStr, prj)
			print "\t%s pull request comments found"%(len(pullRequestComments)),
			if pullRequestComments:
				outData[prj][util.prStr] = {}
				for prComment in pullRequestComments:

					#There are two fields associated with commit 
					commitId = prComment["commit_id"]
					originalCommitId = prComment["original_commit_id"]

					# We try to find an associated commit id in the Travis dataset for both
					jobs = util.find_build_jobs_by_commit(prjData, commitId)
					if jobs.empty:
						jobs = util.find_build_jobs_by_commit(prjData, originalCommitId)

					if not jobs.empty:
						pull_rC = outData[prj][util.prStr]
						for label, job in jobs.iterrows():
							travis_data_row = int(job.row)
							if travis_data_row not in pull_rC:
								pull_rC[travis_data_row] = []
							pull_rC[travis_data_row].append(build_comment_data(prComment, commitId));

						nbMatched=nbMatched+1
				print "\t%s matched"%(nbMatched),
			print ""	

			# Finally, we retrieve issue comments
			# I make the assumption that on GitHub, the issue number corresponds to the pull 
			# request number, if the association exists. This seems to hold true but this is not confirmed.
			nbMatched=0
			issueComments = load_comments(util.issueStr, prj)
			print "\t%s issue comments found"%(len(issueComments)),
			if issueComments:
				outData[prj][util.issueStr] = {}
				for issueComment in issueComments:

					# We can find the pull request number in the url...
					urlParts = issueComment["issue_url"].split("/")
					prNum = int(urlParts[len(urlParts)-1])

					jobs = prjData[prjData.gh_pull_req_num == prNum]
					if not jobs.empty:
						issueC = outData[prj][util.issueStr]
						for label, job in jobs.iterrows():
							travis_data_row = int(job.row)
							if travis_data_row not in issueC:
								issueC[travis_data_row] = []
							issueC[travis_data_row].append(build_comment_data(issueComment, commitId));

						nbMatched=nbMatched+1
							
				print "\t%s matched"%(nbMatched),
			print ""

			lastCompletedPrj = prj
			index = index+1


		print "Fetching completed!"
		print "Duration : %s"%(str(datetime.timedelta(seconds=time.time()-startTime)))
		completed = True

		outData.to_csv(outputfile, sep=';', encoding='utf-8', escapechar='\\')
		os.remove(partialOutputfile)

	except(KeyboardInterrupt, Exception):
		# If an error occured, we dump the recovered data so we don't have to fetch it again
		if not completed and currentPrj:
			# But first, we remove the data concerning the project that didn't complete
			outData.pop(currentPrj, None)
			with open(partialOutputfile, 'w') as outfile:
    				json.dump(outData, outfile)
			print "An error occured. Partial data dumped in %s"%(partialOutputfile)
			print "Relauching this scrpit will retrieve it and try to finish the process."
			#ipdb.set_trace()
		raise # To keep the stack trace