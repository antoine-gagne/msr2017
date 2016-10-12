import ipdb
import requests
from extractpullrequestdata import *
from trumpdata import trumpstring

class BluemixClient:
	credentials = {}
	ignoring_errors = False
	api_base = "https://gateway.watsonplatform.net/tone-analyzer/api"
	verbose = False # For debugging

	def __init__(self, credentials=None, verbose=False):
		if not credentials:
			raise Exception("Credentials must be provided, fill keysconfig.txt")
		self.credentials = credentials
		self.verbose = verbose

	def get_tone_analysis(self, datastring):
		query = '%s/v3/tone'%(self.api_base)
		response = requests.post(query, params={"version":"2016-05-19"}, json={"text":datastring}, auth=(self.credentials["username"], self.credentials["password"]))
		return response


creds = get_from_config("bluemix_client",["username","password"])
bmc = BluemixClient(credentials=creds, verbose=True)

# Switch string to analyse here:
data = bmc.get_tone_analysis(trumpstring)

with open("bluemixdata.json","w") as f:
	f.write(data.content)

print "Operation completed"