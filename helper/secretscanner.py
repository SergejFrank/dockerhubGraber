import json
import re

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class SecretScanner(object):
    def __init__(self,rules_file):
        self._rules = self._load_rules(rules_file)

    def scan(self, string):
        for rule in self._rules:
            if "regex" not in rule:
                continue
            if "id" not in rule:
                continue
            if rule["id"] == "generic-api-key":
                continue
            match = re.compile(rule["regex"]).search(string)
            group = 0
            if "secretGroup" in rule:
               group = rule["secretGroup"]
            if match:
                yield {"type": rule["id"], "secret": match.group(group)}

    def _load_rules(self, rules_file):
        with open(rules_file, 'r') as json_file:
            rules =  json.load(json_file)["rules"]
            return rules

