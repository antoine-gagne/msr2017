from sklearn.linear_model import LinearRegression
import pandas
import statsmodels.formula.api as sm
import ipdb
import matplotlib.pyplot as plt
#regression_analysis.py

def subset_data(d_fail, d_passed, column):
	sub_failed = dfailed[column]
	sub_passed = dpassed[column]

	return sub_failed,sub_passed

file_in = "data/aggregateBluemixTravisDataset.csv"

data = pandas.read_csv(file_in)

data[data["tr_status"]=="passed"] = 1 
data[data["tr_status"]=="errored"] = 0 
data[data["tr_status"]=="failed"] = 0 

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

X = data[[u'anger', u'disgust', u'fear', u'joy', u'sadness', u'analytical', u'confident', u'tentative', u'openness', u'conscientiousness', u'extraversion', u'agreableness', u'emotionalrange']]
Y = data[[u'tr_status']]

result = sm.OLS( Y.astype(bool), X.astype(float) ).fit()
print result.summary()
