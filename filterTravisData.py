# This script is used to filter the travis dataset in order to get the data we need

import ipdb
import ConfigParser
import ghhelper
import json
import pandas
from pprint import pprint

#initial files
travisData = "travistorrent_30_9_2016.csv"
outputfile = "./data/filteredTravisData.csv"

if __name__ == "__main__":

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
	sub = df[travisFields] 
	
	# We only want build jobs with comments
	sub = sub[(sub.gh_num_issue_comments > 0) | (sub.gh_num_commit_comments > 0) | (sub.gh_num_pr_comments > 0)]
	sub = sub.drop_duplicates(subset=["gh_project_name","git_commit"])

	sub.to_csv(outputfile)	

	