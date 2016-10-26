# Project for LOG6307

## Get Started
Run the following

`wget -O travisdata.csv.gz https://travistorrent.testroots.org/dumps/travistorrent_7_9_2016.csv.gz`
`7z x .\data.csv.gz`

fill out the keysconfig with username (from github) and [oauth token](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)

call `python extractpullrequestdata.py`


## Requirements
python
- pandas
- numpy
- ipdb
- requests

## Setting keys up
To protect keys, they are not commited in keysconfig.txt. You should get you own keys from the relevant services:
Github : from https://github.com/settings/tokens, generate a new token and use that in keysconfig.
Bluemix : from your account, find service credentials, and use the username and password provided.

## Process
1/ Run fetchComments (gets the repo, issue and commit comments from github)
2/ Run parseComments (format the comments from the previous step in a single file)
3/ Run filterMergedData (filter the data some more and gets the Bluemix analysis for each issue comment)
4/ Run parseBlueMixData (transforms the raw JSON files from Bluemix into a dataframe for python)