import ipdb
import ConfigParser
import ghhelper
import json
import pandas
import time
import sys
from pprint import pprint

class Util:

	repoStr='repo'
	prStr='pull_r'
	issueStr='issue'

	configFile = "./keysconfig.txt"
	travisData = "travistorrent_30_9_2016.csv"
	filteredTravisData = "./data/filteredTravisData.csv"
	commentsDir = "./data/comments/"
	partialOutputfile = "./data/comments_partial.csv"

	ghc = None

	def __init__(self, github_client):
		self.ghc = github_client

	def find_build_jobs_by_commit(self, data, commitId):
		# Finds the corresponding build jobs in the Travis dataset associated with the specified commit id.
		
		# We first check in the "git_commit" column
		jobs = data[data.git_commit == commitId]

		if jobs.empty:
			# If not found, it may be in the "git_commits" (with an 's') column
			jobs = pandas.DataFrame(columns=list(data.columns.values))
		 	sub = data.git_commits
		 	for label, commitStr in sub.iteritems():
				commits = commitStr.split('#')
				for c in commits:
					if c==commitId:
						jobs.loc[len(jobs)] = data.loc[label]
		
		return jobs

	def get_from_config(config_file, section, config_tags):
		# Reads the configFile file and returns the config tags located in specified section.
		config = ConfigParser.ConfigParser()
		config.read(config_file)
		if isinstance(config_tags,list):
			config_data = {k: config.get(section, k) for k in config_tags}
		else:
			config_data = {config_tags: config.get(section, config_tags)}
		return config_data

	def load_travis_data(self, travis_data_file):
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

		df = pandas.read_csv(travis_data_file)
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

	def fetch_pull_request(self, prj, prNum):
		pullRequest = []
		response = self.ghc.get_pull_requests(prj, prNum)
		if response != None and response.status_code == 200:
			pullRequest = response.json()
		return pullRequest

	def fetch_pull_request_commits(self, prj, prNum):
		commits = []

		response = self.ghc.get_pull_request_commits(prj, prNum)
		if response != None and response.status_code == 200:
			commits = self.fetch_and_append_next_items(commits, response.json())
		
		return [c["sha"] for c in commits]


	def get_next_link(self, response):
		next_link=''
		if "Link" in response.headers:
			links = response.headers["Link"].split(',')
			for l in links:
				link_rel = l.split(';')		
				if "next" in link_rel[1]:
					next_link = link_rel[0].replace('<', '').replace('>', '')
					break;
		return next_link

	def get_last_page(self, response):
		last_page=0
		if "Link" in response.headers:
			links = response.headers["Link"].split(',')
			for l in links:
				link_rel = l.split(';')		
				if "last" in link_rel[1]:
					parts = link_rel[0].split('=')
					last_page = parts[len(parts)-1].replace('>', '')
					break;
		return last_page		

	def fetch_and_append_next_items(self, items, response):
		# There is a max of 100 items that can be returned by GitHub's API
		# The link for the next results are in the response's header
		next = self.get_next_link(response)
		last_page = self.get_last_page(response)
		while next:
			response = self.ghc.make_request(next)		
			if response != None and response.status_code == 200:
				items = items + response.json()
				print "\t%s of approximately %s"%(len(items), int(last_page)*100),
				print "%s"%('\r'),
				next = self.get_next_link(response)
		return items


	def fetch_comments(self, cType, prj):
		comments = []

		if cType == self.repoStr:
			response = self.ghc.get_repo_comments(prj)

		elif cType == self.prStr:
			response = self.ghc.get_pull_request_comments(prj)

		elif cType == self.issueStr:
			response = self.ghc.get_issue_comments(prj)

		if response != None and response.status_code == 200:
			comments = self.fetch_and_append_next_items(response.json(), response)

		return comments