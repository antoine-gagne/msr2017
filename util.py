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

	gch = None

	def __init__(self, github_client):
		self.gch = github_client

	def get_from_config(section, config_tags):
		# Reads the configFile file and returns the config tags located in specified section.
		config = ConfigParser.ConfigParser()
		config.read(configFile)
		if isinstance(config_tags,list):
			config_data = {k: config.get(section, k) for k in config_tags}
		else:
			config_data = {config_tags: config.get(section, config_tags)}
		return config_data

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
			if len(buildJob) > 1: 
				ipdb.set_trace()
			buildJob=buildJob.iloc[0]

		return buildJob

	def fetch_pull_request(prNum):
		pullRequest = []
		response = self.ghc.get_single_pull_request(prNum)
		if response != None and response.status_code == 200:
			pullRequest = response.json()
		return pullRequest


	def fetch_comments(cType, prj):
		comments = []

		if cType == self.repoStr:
			response = self.ghc.get_repo_comments(prj)
			if response != None and response.status_code == 200:
				comments = response.json()

		elif cType == self.prStr:
			response = self.ghc.get_pull_request_comments(prj)
			if response != None and response.status_code == 200:
				comments = response.json()

		elif cType == self.issueStr:
			response = self.ghc.get_issue_comments(prj)
			if response != None and response.status_code == 200:
				comments = response.json()

		return comments