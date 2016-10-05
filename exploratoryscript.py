# Look around the data set
import pandas, numpy
import matplotlib.pyplot as plt
import ipdb

# Opens the csv and break using ipdb so that it can be explored

filename = "travistorrent-5-3-2016.csv"

df = pandas.read_csv(filename)

ipdb.set_trace()

"""

# Examples

# time spent vs time lost vs time wasted
sub = df[["git_branch","gh_project_name","gh_is_pr","tr_status","git_merged_with"]]

# Complexity of a problem vs chance for it to get integrated
sub = df[["gh_num_issue_comments","gh_num_pr_comments", "tr_status"]]
## Only those with at least a comment
subsub = sub[sub["gh_num_pr_comments"]>0]

# failures per loc : Complexity
sub = df[["gh_project_name","gh_sloc","tr_status"]]
x = [sub[sub["gh_project_name"]==x] for x in ["rails/rails", "chef/chef", "jruby/jruby", "rapid7/metasploit-framework"]]

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

sub = df[["gh_project_name","gh_test_lines_per_kloc", "gh_sloc"]]

"""