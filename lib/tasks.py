from __future__ import absolute_import

import sys
import datetime
from lib.celery import app as celery
from pymongo import MongoClient

client = MongoClient()
db = client["files"]
entries = db["entries"]

@celery.task
def _analyze (ID):
    doc = entries.find_one({"_id": ID})

    occurences = {}
    print(doc)
    for char in doc["text"]:
        if char in occurences.keys():
            occurences[char] += 1
        else:
            occurences[char] = 1

    occurences = zip(occurences.values(), occurences.keys())
    print(occurences)
    occurences = [pair for pair in occurences]
    print(occurences)
    occurences.sort()
    print(occurences)
    doc["occurences"] = occurences
    doc["complete"] = True
    entries.save(doc)
    print("Completed indexing for entry given with path {0}".format(doc["path"]))

@celery.task
def _convert (ID):
    doc = entries.find_one({"_id": ID})
    print(doc)
    if doc["path"][-4:] == ".txt":
        try:
            #Opening it in here instead of sending it as a parameter because of a serialization error I was getting.
            file = open(doc["path"])
        except FileNotFoundError as error:
            print("File {0} was not found.\nError:\n{1}\nEnding conversion task.".format(doc["path"], error))
        except:
            print("Unexpected error in opening file {0}.".format(doc["path"]))
            raise
        else:
            #Retrieving every line from the file and processing it to be search-friendly
            #Replaced with spaces to avoid words being conjoined
            #Couldn't replace "\x", getting unicode error
            lines = [line.replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("\v", " ").replace("\b", "").replace("\a", "").replace("\f", " ").replace("\h", "").strip() for line in file if not line == "\n"]
            print(lines)
            #Conjoining the lines into one searchable blob of text
            text = ""
            for index in range(len(lines)):                
                #Don't add an extra space at the top
                if not index == 0:
                    #Spaces stripped from ends of line, adding space so words aren't conjoined
                    text += " "
                text += lines[index]
            #Removing consecutive spaces from the text
            for index in range(len(text)):
                if text[index] == " ":
                    if text[index + 1] == " ":
                        del text[index + 1]
            print(text)
            doc["text"] = text
            entries.save(doc)
            _analyze(ID)
    else:
        print("Format of document at {0} is not currently supported. Please use .txt".format(doc["path"]))

@celery.task
def index (path):
    document = {
        "text": None,
        "occurences": None,
        "path": path,
        "date": datetime.datetime.utcnow(),
        "complete": False
    }
    _convert.delay(entries.insert(document))

@celery.task
def search (phrase):
    pass
    

if __name__ == "__main__":
    print("This file is not meant to be run. Passing execution of command to challenge.py. Please use challenge.py in the future.")
    from sys import argv
    from challenge import run
    run(argv)
