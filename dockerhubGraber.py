from helper.dockerhub import DockerHubClient
from helper.secretscanner import SecretScanner
import argcomplete
import argparse
import mmap
import os
import requests
import json
import config
import random
from itertools import product
import string
import hashlib
from termcolor import colored, cprint

SCANNER = SecretScanner("rules.json")
client = DockerHubClient()
client.login(config.DOCKERHUB_USERNAME,config.DOCKERHUB_PASSWORD)

def displayResults(token, tokenType, searchParam, meta, repo,tag):
    possibleTokenString = '[!] POSSIBLE '+tokenType+' TOKEN FOUND (keyword used:'+searchParam+')'
    print(colored(possibleTokenString,'green'))
    repoString = '[+] Repository URL : '+f'{config.DOCKERHUB_BASE_URL}/{repo["repo_name"]}'
    print(repoString)
    commitString = '[+] Last Pushed: '+meta["last_pushed"]
    print(commitString)
    urlString = '[+] Image : ' + f'{repo["repo_name"]}:{tag}'
    print(urlString)
    tokenString = '[+] Token : ' + token 
    print(tokenString.strip())
    return possibleTokenString+'\n'+commitString+'\n'+urlString+'\n'+tokenString+'\n'+repoString

def createEmptyBinaryFile(name):
    f = open(name, 'wb')
    f.write(1*b'\0')
    f.close()

def initFile(name):
    if not name or not os.path.exists(name):
        createEmptyBinaryFile(name)
        
def writeToWordlist(image, wordlist):
    f = open(wordlist, 'a+')
    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    if s.find(bytes(image,'utf-8')) == -1:
        f.write(image + '\n')


def notifyDiscord(message):
    if not config.DISCORD_WEBHOOKURL:
        print('Please define Discord Webhook URL to enable notifications')
        exit()
    data={}
    data['content']=message
    requests.post(config.DISCORD_WEBHOOKURL,data=json.dumps(data) , headers={"Content-Type": "application/json"})

def notifySlack(message):
    if not config.SLACK_WEBHOOKURL:
        print('Please define Slack Webhook URL to enable notifications')
        exit()
    requests.post(config.SLACK_WEBHOOKURL, json={'text': ':new:'+message})

def notifyTelegram(message):
    if not config.TELEGRAM_CONFIG or not config.TELEGRAM_CONFIG.get("token") or not config.TELEGRAM_CONFIG.get("chat_id"):
        print('Please define Telegram config to enable notifications')
        exit()

    telegramUrl = "https://api.telegram.org/bot{}/sendMessage".format(config.TELEGRAM_CONFIG.get("token"))
    requests.post(telegramUrl, json={'text': message, 'chat_id': config.TELEGRAM_CONFIG.get("chat_id")})

def search_repos(qry, page=1,per_page=100):
    has_next_page = True
    resp = client.search_repos(qry,page,per_page)

    while resp['code'] == 200 and has_next_page:
        for repo in resp['content']['results']:
            yield repo
        if "next" in resp['content']:
            next_page = False
        page = page+1
        resp = client.search_repos(qry,page,per_page)

def get_all_tags(org,repo_name, page=1,per_page=100):
    has_next_page = True
    resp = client.get_tags(org,repo_name,page,per_page)

    while resp['code'] == 200 and has_next_page:
        for repo in resp['content']['results']:
            yield repo
        if "next" in resp['content']:
            next_page = False
        page = page+1
        resp = client.get_tags(org,repo_name,page,per_page)

def searchDockerhub(keywordsFile, args):
    keywords_list = []
    if os.path.exists(keywordsFile):
        keywords_list = open(keywordsFile).read().split("\n")
        random.shuffle(keywords_list)
        print(colored(f'[i] {len(keywords_list)} Keywords loaded from {keywordsFile}', 'yellow'))
        
    
    while True: 
        if keywords_list:
            qry = keywords_list.pop()
        else:
            # This code generates a random string of length between 3 and 5, consisting of uppercase letters, digits, and the characters "-_."
            qry = ''.join(random.choices(string.ascii_uppercase + string.digits + "-_.", k = random.randint(3, 5)))    
        if verbose:
            print(colored(f'[i] Dockerhub query: {config.DOCKERHUB_BASE_URL}/search?q={qry}', 'yellow'))
        
        repos = search_repos(qry)
        for repo in repos:
            if(repo["is_official"]):
                repo_name = repo["repo_name"]
                org = "library"
            else:
                org, repo_name = repo["repo_name"].split("/")     
            tags = get_all_tags(org,repo_name)
            for tag in tags:
                tag_name = tag["name"]
                if verbose:
                    print(colored(f'[i] Scanning: {repo["repo_name"]}:{tag_name}', 'yellow'))
                resp = client.get_images(org,repo_name,tag_name)
                if resp['code'] == 200:
                    images = resp['content']
                    for image in images:
                       
                        instructions = ""
                        if "layers" in image:
                            for layer in image["layers"]:
                                instructions = f"{instructions}\n{layer['instruction']}"
                        for secret in SCANNER.scan(instructions):
                            
                            hash_object = hashlib.sha256(str.encode(secret["secret"]))
                            hex_dig = hash_object.hexdigest()
                            cache_key = f'{org}/{repo_name}:{tag_name} ({hex_dig})'
                            
                            f = open(imagesFile, 'a+', encoding='utf-8')
                            s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                            if s.find(bytes(cache_key,'utf-8')) == -1:
                                
                                
                                displayMessage = displayResults(secret["secret"],secret["type"],qry,image,repo,tag_name)
                                
                                if args.discord:
                                    notifyDiscord(displayMessage)
                                if args.slack:
                                    notifySlack(displayMessage)
                                if args.telegram:
                                    notifyTelegram(displayMessage)
                                f.write(cache_key + '\n')

parser = argparse.ArgumentParser()
argcomplete.autocomplete(parser)
parser.add_argument('-k', '--keyword', action='store', dest='keywordsFile', help='Specify a keywords file (-k keywordsfile.txt)', default="wordlists/keywords.txt")
parser.add_argument('-i', '--images', action='store', dest='imagesFile', help='Create a file where all scanned images are stored',default="rawImages.txt")
parser.add_argument('-d', '--discord', action='store_true', help='Enable discord notifications', default=False)
parser.add_argument('-s', '--slack', action='store_true', help='Enable slack notifications', default=False)
parser.add_argument('-tg', '--telegram', action='store_true', help='Enable telegram notifications', default=False)
parser.add_argument('-v', '--verbose', action='store_true', help='Make the operation more talkative', default=False)
args = parser.parse_args()

keywordsFile = args.keywordsFile
imagesFile = args.imagesFile
verbose = args.verbose
# Init URL file 
initFile(imagesFile)

if verbose:
    print(f"""
{'*' * 90}   
     _            _             _           _      _____           _               
    | |          | |           | |         | |    / ____|         | |              
  __| | ___   ___| | _____ _ __| |__  _   _| |__ | |  __ _ __ __ _| |__   ___ _ __ 
 / _` |/ _ \ / __| |/ / _ \ '__| '_ \| | | | '_ \| | |_ | '__/ _` | '_ \ / _ \ '__|
| (_| | (_) | (__|   <  __/ |  | | | | |_| | |_) | |__| | | | (_| | |_) |  __/ |   
 \__,_|\___/ \___|_|\_\___|_|  |_| |_|\__,_|_.__/ \_____|_|  \__,_|_.__/ \___|_|   

{'*' * 90}
    """)

    cprint("dockerhubGraber", "magenta", end=" ")
    print(" - because who needs privacy anyways? \
We'll find your sensitive data on hub.docker.com \
faster than your boss finds your mistakes.")

searchDockerhub(keywordsFile, args)
