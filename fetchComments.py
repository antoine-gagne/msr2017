# This script is used to extract comments on pull requests from Github.
# It gets everything and writes it to the specified file

import ipdb
import ConfigParser
import ghhelper
import json
import pandas
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
		buildJob = None
	 	sub = data.git_commits
	 	for i in range(len(sub)):
			commits = sub[i].split('#')
			b = next((c for c in commits if c==commitId), None)
			if b != None:
				buildJob = data.loc[i]				
				break
	else:
		buildJob = buildJob.iloc[0]		

	return buildJob



if __name__ == "__main__":

	# Init github client
	creds = get_from_config("gh_client",["username","oauth_token"])
	ghc = ghhelper.GithubClient(credentials=creds, verbose=True)
	td = load_travis_data()

	projectNames = td["gh_project_name"]
	projectNames = projectNames.drop_duplicates()

	#garg = find_build_job(td, "20403b8040e70ba23de28446efd22fb5a82a481b")
	#garg = find_build_job(td, "6f88fd4fb3ca219337e75e16f22dcd88ad7ee7d1")

	dfColumns = list(td.columns.values)
	headers = [
		# "git_commit",
		# "gh_real_num_commit_comments", 
		# "gh_real_num_pr_comments", 
		# "gh_real_num_issue_comments",
		"gh_comment_id",
		"gh_comment_type",
		"gh_created_at",
		"gh_updated_at",
		"gh_user_id",
		"gh_user_login",
		"gh_body",
		"gh_body_text",
		"gh_body_html"
	]
	dfColumns.extend(headers)
 	outData = pandas.DataFrame(columns=dfColumns)

	ipdb.set_trace()

  	# We need to find the comments for each commit id
  	for index, prj in projectNames.iteritems():
  		print "Progress : %s/%s"%(index,len(projectNames))

  		prjData = td[td.gh_project_name == prj]

  		# We retrieve all comments for the project.
		repoComments = ghc.get_repo_comments(prj).json()

		ipdb.set_trace()

		if len(repoComments)!=0:
			for commentData in repoComments:
				ipdb.set_trace()
				commitId = commentData["commit_id"]
				job = find_build_job(prjData, commitId)
				if job != None:
					data = [
						commentData["id"],
						"repo",
						commentData["created_at"],
						commentData["updated_at"],
						commentData["user"]["id"],
						commentData["user"]["login"],
						commentData["body"],
						commentData["body_text"],
						commentData["body_html"]
					]				
					outData.add(td[index].combine(data))

		# pullRequestComments = ghc.get_pull_request_comments(prj).json()
		# issueComments = ghc.get_issue_comments(prj).json()
		# for i in range(len(pullRequestComments)):
		# 	commentData = pullRequestComments[i].json()


		# for i in range(len(issueComments)):
		# 	commentData = issueComments[i].json()
				


	