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

	def fetch_pull_request(self, prNum):
		pullRequest = []
		response = self.ghc.get_single_pull_request(prNum)
		if response != None and response.status_code == 200:
			pullRequest = response.json()
		return pullRequest


	def fetch_comments(self, cType, prj):
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