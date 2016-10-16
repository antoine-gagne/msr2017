import requests
from time import sleep
import ipdb

# TODO Move this to some utils file

def AsJSON(apiresponse):
	return json.loads(apiresponse.content)


class GithubClient:

	credentials = {}
	ignoring_errors = False
	api_base = "https://api.github.com"
	default_headers = {'User-Agent': "LOG6307-team-project", 'Accept': 'application/vnd.github.v3.raw+json'}
	verbose = False # For debugging
	nbRequestsMade = 0;

	def __init__(self, credentials=None, verbose=False, ignoring_errors=False):
		if not credentials:
			raise Exception("Credentials must be provided, fill keysconfig.txt")
		self.credentials = credentials
		self.verbose = verbose
		self.ignoring_errors = ignoring_errors

	def make_request(self, resource_uri, headers=''):

		if not headers:
			headers = self.default_headers		

		# Sign and make request
		if self.verbose:
			print "Fetching %s" % resource_uri
		auth=(self.credentials["username"], self.credentials["oauth_token"])
		response = requests.get(resource_uri, auth=auth, headers=headers)

		if response.status_code == 404:
			response = None
		elif response.status_code != 200:
			if not self.ignoring_errors:
				print "Status code returned was not 200, setting breakpoint. set ignoring_errors to True to ignore and keep going"
				ipdb.set_trace()
			else:
				print "Status code : %s\tContent : %s"%(response.status_code, response.text)
		sleep(0.1)
		self.nbRequestsMade = self.nbRequestsMade+1
		return response

	# Specific resources begin here
	def get_pull_request_for_repo(self, user_repo):
		query = '%s/repos/%s/pulls?state=all&per_page=100'%(self.api_base, user_repo)
		response = self.make_request(query)
		return response

	def get_single_pull_request(self, user_repo, pull_id):
		query = '%s/repos/%s/pulls/%s'%(self.api_base, user_repo, int(pull_id))
		response = self.make_request(query)
		return response

	def get_repo_comments(self, user_repo):
		query = "%s/repos/%s/comments?per_page=100"%(self.api_base,user_repo)
		response = self.make_request(query)
		return response

	def get_pull_request_comments(self, user_repo):
		query = "%s/repos/%s/pulls/comments?per_page=100"%(self.api_base,user_repo)
		response = self.make_request(query)
		return response

	def get_pull_request_commits(self, user_repo, pull_id):
		query = "%s/repos/%s/pulls/%s/commits?per_page=100"%(self.api_base,user_repo, pull_id)
		response = self.make_request(query)
		return response

	def get_issue_comments(self, user_repo):
		query = "%s/repos/%s/issues/comments?per_page=100"%(self.api_base,user_repo)
		response = self.make_request(query)
		return response

	def get_single_commit(self, user_repo, commit_sha):
		query = "%s/repos/%s/git/commits/%s"%(self.api_base,user_repo,commit_sha)
		response = self.make_request(query)
		return response

	def check_rate_limit(self):
		query = "%s/rate_limit?"%(self.api_base)
		response = self.make_request(query)
		return response
