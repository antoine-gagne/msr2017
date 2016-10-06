import requests
import ipdb

# TODO Move this to some utils file

def AsJSON(apiresponse):
	return json.loads(apiresponse.content)


class GithubClient:

	credentials = {}
	api_base = "https://api.github.com"
	verbose = False # For debugging

	def __init__(self, credentials, verbose=False):
		self.credentials = credentials
		self.verbose = verbose

	def make_request(self, resource_uri):
		# Check Request limit sign request, etc...
		# Possibly need to iterate through pages
		if self.verbose:
			print "Fetching %s" % resource_uri
		response =  requests.get(resource_uri)
		return response

	# Specific resources begin here
	def get_pull_request_for_repo(self, user_repo):
		query = '%s/repos/%s/pulls?client_id=%s&client_secret=%s'%(self.api_base, user_repo, self.credentials["client_id"], self.credentials["client_secret"])
		response = self.make_request(query)
		return response

	def get_single_pull_request(self, user_repo, pull_id):
		query = '%s/repos/%s/pulls/%s?client_id=%s&client_secret=%s'%(self.api_base, user_repo, pull_id, self.credentials["client_id"], self.credentials["client_secret"])
		response = self.make_request(query)
		return response
