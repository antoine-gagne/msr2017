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
	verbose = False # For debugging

	def __init__(self, credentials=None, verbose=False):
		if not credentials:
			raise Exception("Credentials must be provided, fill keysconfig.txt")
		self.credentials = credentials
		self.verbose = verbose

	def make_request(self, resource_uri):
		# Sign and make request
		if self.verbose:
			print "Fetching %s" % resource_uri
		response = requests.get(resource_uri, auth=(self.credentials["username"], self.credentials["oauth_token"]))
		if response.status_code == 404:
			response = None
		elif response.status_code != 200 and not self.ignoring_errors:
			print "Status code returned was not 200, setting breakpoint. set ignoring_errors to True to ignore and keep going"
			ipdb.set_trace()
		sleep(0.1)
		return response

	# Specific resources begin here
	def get_pull_request_for_repo(self, user_repo):
		query = '%s/repos/%s/pulls'%(self.api_base, user_repo)
		response = self.make_request(query)
		return response

	def get_single_pull_request(self, user_repo, pull_id):
		query = '%s/repos/%s/pulls/%s'%(self.api_base, user_repo, int(pull_id))
		response = self.make_request(query)
		return response

	def get_single_pull_request_comments(self, user_repo, pull_id):
		query = "%s/repos/%s/issues/%s/comments"%(self.api_base,user_repo,int(pull_id))
		response = self.make_request(query)
		return response

	def check_rate_limit(self):
		query = "%s/rate_limit?"%(self.api_base)
		response = self.make_request(query)
		return response
