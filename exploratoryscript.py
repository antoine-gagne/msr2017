# Look around the data set
import pandas, numpy
import matplotlib.pyplot as plt
import ipdb

filename = "travistorrent-5-3-2016.csv"


def plot_histo_nominal(data):
	data.value_counts().plot(kind='bar')
	plt.show()

def plot_histo(data):
	data.hist()
	plt.show()


df = pandas.read_csv(filename)

ipdb.set_trace()



"""
# histogram of nominal data
plot_histo_nominal(df.tr_status)

# histo of numeric data
plot_histo(df.gh_sloc)

# max amount developpers on projects (filtering for small projects)
sub = df[["gh_project_name","gh_team_size"]]
sub = sub[sub["gh_team_size"]<20]
data = sub.groupby("gh_project_name").agg(['max']) 
data.gh_team_size.hist()

# Nb of lines of code per project by nb of devs
sub = df[["gh_project_name","gh_sloc","git_num_committers"]]
data = sub.groupby("gh_project_name").agg(['max'])
plt.scatter(data["git_num_committers"],data["gh_sloc"])

"""