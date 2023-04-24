<img src="https://img.shields.io/badge/made%20with-python-blue.svg" alt="made with python 3.x"> <img src="https://img.shields.io/github/issues/SergejFrank/dockerhubgraber.svg">
# About dockerhubGraber

**dockerhubGraber is a tool developed in Python3 to monitor dockerhub to search and find sensitive data for various online services. such as: Github, Amazon (AWS), Mailgun, Discord, Twitter, Heroku, Stripe, Twilio...**

![demo](images/preview-dockerhubgraber.png)

## How it works ?


## Usage

``````````
usage: dockerhubGraber.py [-h] [-k KEYWORDSFILE] [-i IMAGESFILE] [-d] [-s] [-tg] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -k KEYWORDSFILE, --keyword KEYWORDSFILE
                        Specify a keywords file (-k keywordsfile.txt)
  -i IMAGESFILE, --images IMAGESFILE
                        Create a file where all scanned images are stored
  -d, --discord         Enable discord notifications
  -s, --slack           Enable slack notifications
  -tg, --telegram       Enable telegram notifications
  -v, --verbose         Make the operation more talkative
``````````

## Dependencies

dockerhubGraber needs some dependencies, to install them on your environment:

``pip3 install -r requirements.txt``

## Configuration

Before your start **dockerhubGraber** you need to modify the configuration file ``config.py`` :

## TODO

- [X] Manage rate limit
- [X] Add multi threads

## Resources

The code of the project was largely inspired by [gitGraber](https://github.com/hisxo/gitGraber/). thanks for the great work. i hope this tool will make a similar contribution to the security of dockerhub.

# Disclaimer

This project is made for educational and ethical testing purposes only. Usage of this tool for attacking targets without prior mutual consent is illegal. Developers assume no liability and are not responsible for any misuse or damage caused by this tool.
