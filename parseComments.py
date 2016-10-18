# This script is used to fetch comments on several projects from Github.
# It gets all 3 types of comments (commits, issues and pull requests) and writes 
# the raw JSOn data to a file

import ipdb
import ConfigParser
import ghhelper
import numpy
import util
import json
import pandas
import sys
import os
import datetime
import time
import signal
from pprint import pprint

configFile = "./keysconfig.txt"
def get_from_config(config_file, section, config_tags):
		# Reads the configFile file and returns the config tags located in specified section.
		config = ConfigParser.ConfigParser()
		config.read(config_file)
		if isinstance(config_tags,list):
			config_data = {k: config.get(section, k) for k in config_tags}
		else:
			config_data = {config_tags: config.get(section, config_tags)}
		return config_data

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

def load_comments(dir, commentsType, project):
	comments = []
	path = "%s%s/%s.json"%(dir, project, commentsType)
	try:
		if os.path.isfile(path):
			with open(path) as jsonFile:    
	    			comments = json.load(jsonFile)
	except:
		print "Cannot load file : %s"%(path)
	return comments

def append_comments_to_output(outputData, matched, commentsColumn, commentsNbColumn):

	for travis_data_row, comment_data in matched.iteritems():

		sortedComments = sorted(comment_data, key=lambda k: k['gh_comment_id'])

		comments = "".join(map(lambda c: "<COMMENT>%s : %s"%(c["gh_user_login"], " ".join(c["gh_body"].splitlines()) ), sortedComments))
		
		# We remove the csv separator char
		comments = comments.replace(";", "<semicolon>")

		if travis_data_row not in outData.index:
			outData.loc[travis_data_row] = td.loc[travis_data_row]
		
		assert numpy.isnan(outData.loc[travis_data_row, commentsColumn])
		outData.loc[travis_data_row, commentsNbColumn] = len(sortedComments)
		outData.loc[travis_data_row, commentsColumn] = comments



if __name__ == "__main__":

	# Init github client
	creds = get_from_config(configFile, "gh_client",["username","oauth_token"])
	util = util.Util(None)

	commentsDir = util.commentsDir

	print "Loading Travis data..."
	td = util.load_travis_data(util.filteredTravisData)

	projectNames = td["gh_project_name"]
	projectNames = projectNames.drop_duplicates()
	projectNames = projectNames.sort_values()

	# We check if there is already a file partially created from a previous run
	outDataColumns = list(td.columns.values) + [
			"gh_repo_comments", 
			"gh_repo_comments_num",
			"gh_pr_comments", 
			"gh_pr_comments_num",
			"gh_issue_comments",
			"gh_issue_comments_num"
	]
	outData	= pandas.DataFrame(columns=outDataColumns)

	# We set a matching index for convenience
	td = td.set_index('row')
	outData = outData.set_index('row')

	completed=False
	startTime = time.time()
  	print "Parsing comments..."
  	index=0
  	for label, prj in projectNames.iteritems():

  		print "Progress : %s/%s : parsing comments for %s"%(index,len(projectNames),prj)
  		prjData = td[td.gh_project_name == prj]

  		#if index == 5: break

  		# We first get all repo comments
  		nbMatched=0
		repoComments = load_comments(commentsDir, util.repoStr, prj)
		print "\t%s repo comments found"%(len(repoComments)),
		if repoComments:
			matched = {}
			for repoComment in repoComments:
				
				commitId = repoComment["commit_id"]

				# We try to find an associated commit id in the Travis dataset
				jobs = util.find_build_jobs_by_commit(prjData, commitId)
				if not jobs.empty:
					for travis_data_row, job in jobs.iterrows():
						if travis_data_row not in matched:
							matched[travis_data_row] = []
						matched[travis_data_row].append(build_comment_data(repoComment, commitId));
					nbMatched=nbMatched+1

			append_comments_to_output(outData, matched, "gh_repo_comments", "gh_repo_comments_num")

			print "\t%s matched"%(nbMatched),
		print ""

		# We then get all pull request comments
		nbMatched=0
		pullRequestComments = load_comments(commentsDir, util.prStr, prj)
		print "\t%s pull request comments found"%(len(pullRequestComments)),
		if pullRequestComments:
			matched = {}
			for prComment in pullRequestComments:

				commitId = prComment["commit_id"]
				jobs = util.find_build_jobs_by_commit(prjData, commitId)
				
				# Sometime there is another commit id field called original_commit_id
				if jobs.empty and "original_commit_id" in prComment:
					originalCommitId = prComment["original_commit_id"]
					jobs = util.find_build_jobs_by_commit(prjData, originalCommitId)


				if not jobs.empty:
					for travis_data_row, job in jobs.iterrows():
						if travis_data_row not in matched:
							matched[travis_data_row] = []
						matched[travis_data_row].append(build_comment_data(prComment, commitId));
					nbMatched=nbMatched+1

			append_comments_to_output(outData, matched, "gh_pr_comments", "gh_pr_comments_num")

			print "\t%s matched"%(nbMatched),
		print ""	

		# Finally, we retrieve issue comments
		# I make the assumption that on GitHub, the issue number corresponds to the pull 
		# request number, if the association exists. This seems to hold true but this is not confirmed.
		nbMatched=0
		issueComments = load_comments(commentsDir, util.issueStr, prj)
		print "\t%s issue comments found"%(len(issueComments)),
		if issueComments:
			matched = {}
			for issueComment in issueComments:

				# We can find the pull request number in the url...
				urlParts = issueComment["issue_url"].split("/")
				prNum = int(urlParts[len(urlParts)-1])

				jobs = prjData[prjData.gh_pull_req_num == prNum]
				if not jobs.empty:
					for travis_data_row, job in jobs.iterrows():
						if travis_data_row not in matched:
							matched[travis_data_row] = []
						matched[travis_data_row].append(build_comment_data(issueComment, commitId));
					nbMatched=nbMatched+1

			append_comments_to_output(outData, matched, "gh_issue_comments", "gh_issue_comments_num")

			print "\t%s matched"%(nbMatched),
		print ""

		
		# We can format the matched comments in the output data


		index = index+1

	print "Parsing completed!"
	print "Duration : %s"%(str(datetime.timedelta(seconds=time.time()-startTime)))

	outData.to_csv("./data/mergedData.csv", sep=';', encoding='utf-8')
