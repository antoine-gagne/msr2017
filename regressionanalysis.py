import pandas
import statsmodels.formula.api as sm
import ipdb
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

def subset_data(d_fail, d_passed, column):
	sub_failed = dfailed[column]
	sub_passed = dpassed[column]

	return sub_failed,sub_passed

# Desired analysis, histo, regression, mann-whit, stats-compare
algo = "stats_compare"

file_in = "data/aggregateBluemixTravisDataset.csv"

data = pandas.read_csv(file_in)

data_pass = pandas.DataFrame.copy(data[data["tr_status"]=="passed"])
data_fail = pandas.DataFrame.copy(data[data["tr_status"]=="failed"])
data = pandas.concat([data_pass, data_fail])
data.loc[data.tr_status == "passed", 'tr_status'] = 1
data.loc[data.tr_status == "failed", 'tr_status'] = 0

"""
data[data["tr_status"]=="failed"] = 0 
data[data["tr_status"]=="passed"] = 1 
data = data.drop(data["tr_status"]=="errored")
data = data.drop(data["tr_status"]=="")
#data[data["tr_status"]=="errored"] = 0 
"""

# dfailed = data[data["tr_status"]=="failed"]
# derror = data[data["tr_status"]=="error"]
# dfailed = pandas.concat([dfailed,derror])
# dpassed = data[data["tr_status"]=="passed"]

"""
u'Unnamed: 0', u'row', u'tr_build_id', u'tr_build_number',
u'tr_num_jobs', u'tr_jobs', u'tr_job_id', u'tr_status', u'tr_duration',
u'tr_started_at', u'tr_tests_ran', u'tr_tests_failed',
u'gh_project_name', u'gh_lang', u'gh_team_size', u'git_num_committers',
u'gh_sloc', u'git_commit', u'git_num_commits', u'git_commits',
u'gh_by_core_team_member', u'gh_is_pr', u'gh_pull_req_num',
u'gh_description_complexity', u'gh_repo_comments',
u'gh_repo_comments_num', u'gh_pr_comments', u'gh_pr_comments_num',
u'gh_issue_comments', u'gh_issue_comments_num', u'comment', u'anger',
u'disgust', u'fear', u'joy', u'sadness', u'analytical', u'confident',
u'tentative', u'openness', u'conscientiousness', u'extraversion',
u'agreableness', u'emotionalrange'],
"""

# plt.boxplot(subset_data(dfailed,dpassed,"joy"),labels = ['failed',"passed"])
# plt.show()


if algo == "histo":
	X = data[["tr_status", u'anger', u'disgust', u'fear', u'joy', u'sadness', u'analytical', u'tentative', u'openness', u'conscientiousness', u'extraversion', u'agreableness', u'emotionalrange']]
	X.groupby("tr_status").hist()
	axes = plt.gca()
	axes.set_xlim([0,1])
	plt.show()

if algo == "regression":
	X = data[[ u'anger', u'disgust', u'fear', u'joy', u'sadness', u'analytical', u'tentative', u'openness', u'conscientiousness', u'extraversion', u'agreableness', u'emotionalrange']]
	X = data[[ u'anger', u'fear', u'joy', u'sadness', u'analytical', u'tentative', u'openness', u'conscientiousness', u'extraversion', u'agreableness', u'emotionalrange']]

	"""
	bins_emotional = [0,0.5,0.75,1]
	bins_social = [0,0.25,0.75,1]
	bins_language = [0,0.25,0.75,1]

	labels = [1,2,3]
	# Discretization, uncomment to discretize data according to suggested bins
	for cat in ["anger", "disgust", 'fear', 'joy', 'sadness']:
		# X[cat] = pandas.cut(X[cat], bins_emotional,labels = labels)
		X.loc[X[cat] <= bins_emotional[1] , cat] = 1
		X.loc[X[cat] <= bins_emotional[2] , cat] = 2
		X.loc[X[cat] < bins_emotional[3] , cat] = 3

	for cat in ["analytical", 'tentative']:
		# X[cat] = pandas.cut(X[cat], bins_social, labels = labels)
		X.loc[X[cat] <= bins_social[1] , cat] = 1
		X.loc[X[cat] <= bins_social[2] , cat] = 2
		X.loc[X[cat] < bins_social[3] , cat] = 3
	for cat in ['openness', 'conscientiousness', 'extraversion', 'agreableness', 'emotionalrange']:
		# X[cat] = pandas.cut(X[cat], bins_language, labels = labels)
		X.loc[X[cat] <= bins_language[1] , cat] = 1
		X.loc[X[cat] <= bins_language[2] , cat] = 2
		X.loc[X[cat] < bins_language[3] , cat] = 3
	"""
	Y = data[[u'tr_status']]
	result = sm.OLS( Y.astype(float), X.astype(float) ).fit()
	print result.summary()

if algo == "mann-whit":
	feature_list = [ u'anger', u'disgust', u'fear', u'joy', u'sadness', u'analytical', u'tentative', u'openness', u'conscientiousness', u'extraversion', u'agreableness', u'emotionalrange']
	x1 = X[X["tr_status"] == 0]
	x2 = X[X["tr_status"] == 1]

	for cat in feature_list:
		try:
			result2 = plt.hist(x1[cat]-x2[cat])
			print cat
			plt.show()
		except:
			print "failed for %s"%cat

if algo == "stats_compare":
	X = data[["tr_status", u'anger', u'disgust', u'fear', u'joy', u'sadness', u'analytical', u'tentative', u'openness', u'conscientiousness', u'extraversion', u'agreableness', u'emotionalrange']]
	x1 = X[X["tr_status"] == 0]
	x2 = X[X["tr_status"] == 1]
	print x1.describe()
	print x2.describe()