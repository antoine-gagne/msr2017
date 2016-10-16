# This script is used to fetch comments on several projects from Github.
# It gets all 3 types of comments (commits, issues and pull requests) and writes 
# the raw JSOn data to a file

import ipdb
import ConfigParser
import ghhelper
import util
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
	# TODO : Investigate why there are duplicates... 
	# This could indicates that they did not parsed their data correctly
	travisFields = 	[
			"row",
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

def build_comment_data(cData, job, commitId, cType, reactions=""):
	ipdb.set_trace()
	data = [
		job.row,
		job.git_commit,
		commitId,
		job.gh_pull_req_num,
		cData["id"],
		cType,
		cData["created_at"],
		cData["updated_at"],
		cData["user"]["id"],
		cData["user"]["login"],
		cData["body"],
		reactions]
	return data;


if __name__ == "__main__":

	# Init github client
	creds = get_from_config("gh_client",["username","oauth_token"])
	ghc = ghhelper.GithubClient(credentials=creds, ignoring_errors=True)
	util = util.Util(ghc)

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

  	#DEBUG
  	#======
  	projectNames = td[td["gh_project_name"] == "Albacore/albacore"]
  	projectNames = projectNames["gh_project_name"]
  	projectNames = projectNames.drop_duplicates()
  	#ipdb.set_trace()
	#======

  	# We fetch the raw json comment data
  	print "Fetching comments..."
  	index=0
  	for label, prj in projectNames.iteritems():
  		print "Progress : %s/%s : fetching comments for %s"%(index,len(projectNames),prj)

  		prjData = td[td.gh_project_name == prj]
  		
  		# We first get all repo comments
		repoComments = util.fetch_comments(CommentType.REPO, prj)
		for commentData in repoComments:
			commitId = commentData["commit_id"]

			# We try to find an associated commit id in the Travis dataset
			job = util.find_build_job_by_commit(prjData, commitId)
			if not job.empty:
				outData.loc[len(outData)] = build_comment_data(commentData, job, util.repoStr);

		# We then get all pull request comments
		pullRequestComments = util.fetch_comments(CommentType.PULL_REQUEST, prj)
		for prComment in pullRequestComments:

			#There are two fields associated with commit 
			commitId = prComment["commit_id"]
			originalCommitId = prComment["original_commit_id"]

			# We try to find an associated commit id in the Travis dataset for both
			job = util.find_build_job_by_commit(prjData, commitId)
			if job.empty:
				job = util.find_build_job_by_commit(prjData, originalCommitId)

			if not job.empty:
				outData.loc[len(outData)] = build_comment_data(prComment, job, commitId, util.prStr);				

		# Finally, we retrieve issue comments
		# The process is a little more complicated because there isn't any info about commits in them.
		# Also, I make the assumption that on GitHub, the issue number corresponds to the pull 
		# request number, if the association exists. This seems to hold true this is not confirmed.
		issueComments = fetch_comments(CommentType.ISSUE, prj)
		for issueComment in issueComments:

			# We can find the pull request number in the url...
			urlParts = issueComment["issue_url"].split("/")
			prNum = int(urlParts[len(urlParts)-1])

			# We retrieve the associated pull request, if it exists.
			pullRequest = util.fetch_pull_request(prNum)
			if pullRequest.empty:
				continue

			commitId = pullRequest["merge_commit_sha"]

			# We try to find an associated commit id in the Travis dataset for both
			job = util.find_build_job_by_commit(prjData, commitId)
			if not job.empty:
				outData.loc[len(outData)] = build_comment_data(issueComment, job, commitId, util.issueStr);


		# We wait the specified amount of time if the api request limit is reached
		if ghc.nbRequestsMade >= limit:
			waitTime = resetTime - time.time() + 10
			print "GitHub api request limit reached. The limit will be reset in %s seconds"%(waitTime)
			while waitTime > 0:
				print "%s seconds remaining..."%(waitTime)
				sleep(min(10*60, waitTime))
				waitTime = waitTime - 10*60
		index=index+1


	# We can finally write the data to a csv file
	try:
		outData.to_csv(outputfile)
	except:
		ipdb.set_trace()


	