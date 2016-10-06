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