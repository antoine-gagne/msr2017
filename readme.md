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


## Current process
1/ Read the TravisTorrentdata
2/ Filter to keep pull requests with more than 5 comments (in addition to the original pull request comment)
3/ Call Github API to fetch the initial comment and follow up comments. If comments cannot be found (some projects were deleted since the project was released), store empty string. Save that to intermediate CSV file (pullreqdata.csv, use `pandas.read_csv("pullreqdata.csv")` to open).
4/ TODO Plug in the comments in the Bluemix API to get their tone analysis
5/ TODO Analyse that


Proposals:

1. Downloader les comments sur les pull requests (accès via API GH), Utiliser Bluemix Alchemy API pour analyser le contenu des comment threads.

2. Dead-end branches, time invested vs time lost vs time wasted. Nécessite d'aller voir si les pull requests ont été acceptés ou non (ca semble pas être disponible dans le travistorrent)

3. A voir.