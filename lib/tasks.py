#This file is only to be run by celery

from __future__ import absolute_import

import datetime

import json

from lib.celery import app as celery

from pymongo import MongoClient

#Access the database for the files

client = MongoClient()

db = client["files"]

entries = db["entries"]

SUPPORTED_FORMATS  = ".txt or .json"

#Tasks

#_convert_txt and _convert_json are launched by index to parse the file and optimize it for searchability.

@celery.task
def _convert_txt (ID):
    doc = entries.find_one({"_id": ID})

    #In case the search fails
    if not doc:
        print("Problem opening document with id {0}, exiting...".format(ID))
        return

    try:
        #Automatically opens in read only mode
        file = open(doc["path"])

    except FileNotFoundError as error:
        print("File {0} was not found.\nError:\n{1}\nEnding conversion task.".format(doc["path"], error))

    except:
        print("Unexpected error in opening file {0}.".format(doc["path"]))

        raise

    else:
        '''Retrieving every line from the file and processing it to be search-friendly
        Replaced with spaces to avoid words being conjoined'''
        #Couldn't replace "\x", getting unicode error
        #Including the line above in the multi-line comment was causing an error
        lines = [line.replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("\v", " ").replace("\b", "").replace("\a", "").replace("\f", " ").replace("\h", "").strip() for line in file if not line == "\n"]

        #Conjoining the lines into one searchable lump of text
        text = " ".join(lines)

        #Removing consecutive spaces from the text
        while not text.find("  ") == -1:
            #Couldn't use str.replace("  ", " "), would result in never exiting loop.
            split = text.partition("  ")

            text = " ".join([split[0], split[2]])

        doc["text"] = text

        doc["complete"] = True

        print(doc)

        entries.save(doc)

        file.close()

        print("Completed indexing for entry given with path {0}".format(doc["path"]))



@celery.task
def _convert_json (entry, path, fileName):
    doc = {
        "title": entry["title"],

        #Simply the name of the file
        "name": fileName,

        "text": entry["text"],

        "tags": entry["tags"],

        #Path the file relative to the directory of indexsearch.py or absolute
        "path": path,

        #Time of indexing
        "date": datetime.datetime.utcnow(),
        
        #Used to prevent this document from being searched before _convert_txt finishes this entry, not necessary here
        "complete": True
    }

    entries.insert(doc)



#Task called by command line interface to index files for searching.
@celery.task
def index (path, meta):
    #Forward slashes will always work with open()
    path.replace("\\", "/")

    #Ensuring that important fields are text searchable by Mongo and weighting their importance
    entries.ensure_index([("title", "text"), ("name", "text"), ("text", "text"), ("tags", "text")], weights={"title": 10, "name": 10, "text": 1, "tags": 5})

    #Retrieving the name of the file and its extension
    fileName = path[path.rfind("/") + 1:]

    #Creating a string out of the tags given to the file
    tags = " ".join(meta["tags"])

    #Currently just setting it up to handle .txt and .json formats. Easy to expand to include other formats but want to get this submitted ASAP

    #Handle .txt files
    if path[-4:] == ".txt":

        document = {
            #Can be "", optional
            "title": meta["title"],

            #Simply the name of the file
            "name": fileName,

            #Text is parsed then added by _convert_txt task
            "text": "",

            #If tags are given then they end up in a string with a space delimeter here
            "tags": tags,

            #Path the file relative to the directory of indexsearch.py or absolute
            "path": path,

            #Time of indexing
            "date": datetime.datetime.utcnow(),
        
            #Used to prevent this document from being searched before _convert_txt finishes this entry
            "complete": False
        }

        #Inserts the document and sends the _id to _convert
        _convert.delay(entries.insert(document))

    #Handle .json files
    elif path[-5:] == ".json":
        try:
            #Automatically opens in read only mode
            file = open(path)

        except FileNotFoundError as error:
            print("File {0} was not found.\nError:\n{1}\nEnding conversion task.".format(path, error))

        except:
            print("Unexpected error in opening file {0}.".format(path))

            raise

        else:
            #Using python's json module
            json_file = json.load(file)

            if "entries" in json_file.keys():
                if type(json_file["entries"]) is list:
                    for entry in json_file["entries"]:
                        if "title" in entry.keys() and "text" in entry.keys() and "tags" in entry.keys():
                            _convert_json(entry, path, fileName)

                        else:
                            print("Entry {0} in file at path {1} did not have all required fields, out of title, text and tags".format(entry, path))

                else:
                    print("File at path {0} did not follow the template for json files, value for key 'entries' was not a list/array".format(path))

            else:
                print(".json file at {0} did not have required keys 'title', 'text', and 'tags'.".format(doc["path"]))

            file.close()

    else:
        print("Format of document at {0} is not currently supported. Please use ".format(doc["path"]) + SUPPORTED_FORMATS)



#Task used to search all file entries and return results
@celery.task
def search (phrase, sort="relevance", resultFilter=None, filterData=None):
    #Turns the Mongo query results into readable results to send back to the command line interface.
    def results (matches, sort, resultFilter, filterData):
        #If the search turns up any results...
        if len(matches) > 0:
            #Stores all the strings sent back to command line
            results = []

            if not sort == "relevance":
                if sort == "date-new":
                    if len(matches) > 1:
                        #Create a list of the dates of each entry to sort with...
                        dates = []
                        
                        for match in matches:
                            dates.append(match["obj"]["date"])

                        #Create a zip object of two-tuples, t[0] = date, t[1] = match
                        matches = zip(dates, matches)

                        #Extracting the two-tuples from the zip object into a list
                        matches = [pair for pair in matches]

                        #Sorts based on the first element of the two-tuple, the date. Smallest to largest (Oldest to newest)
                        matches.sort()
                        
                        #Same as date-old but everything gets reversed
                        matches.reverse()

                        #Taking just the match object of the two-tuple with the date
                        matches = [match[1] for match in matches]
                
                elif sort == "date-old":
                    if len(matches) > 1:
                        #Create a list of the dates of each entry to sort with...
                        dates = []
                        
                        for match in matches:
                            dates.append(match["obj"]["date"])

                        #Create a zip object of two-tuples, t[0] = date, t[1] = match
                        matches = zip(dates, matches)

                        #Extracting the two-tuples from the zip object into a list
                        matches = [pair for pair in matches]

                        #Sorts based on the first element of the two-tuple, the date. Smallest to largest (Oldest to newest)
                        matches.sort()

                        #Taking just the match object of the two-tuple with the date
                        matches = [match[1] for match in matches]

                else:
                    raise NotImplementedError("Sort method {0} has not been implemented.".format(sort))

            if resultFilter == "type":
                #Keeps indexes of matches that are scrubbed out by the filter
                filtered = []

                for index in range(len(matches)):
                    match = matches[index]

                    if not match["obj"]["name"].find(".") == -1:
                        #Matching the file extension
                        for extensionFilter in filterData:
                            if not match["obj"]["name"][match["obj"]["name"].rfind("."):] == extensionFilter:
                                filtered.append(index)

                #Highest indexes first
                filtered.reverse()

                #Delete filtered results
                for index in filtered:
                    del matches[index]

            #Create a report for each result
            for index in range(len(matches)):
                match = matches[index]

                if sort == "relevance":
                    #If the entry was given a title, use it otherwise only the file path.
                    results.append("{0} - Match Coefficient: {1}\n".format(match["obj"]["title"] + " (" + match["obj"]["path"] + ")" if not match["obj"]["title"] == "" else match["obj"]["path"], match["score"]))

                elif sort == "date-new" or sort == "date-old":
                    #If the entry was given a title, use it otherwise only the file path.
                    results.append("{0} - Date indexed: {1}\n".format(match["obj"]["title"] + " (" + match["obj"]["path"] + ")" if not match["obj"]["title"] == "" else match["obj"]["path"], match["obj"]["date"]))

            #If all results got removed by the filter...
            if len(results) < 1:
                results = "No matches found for search of {0}\n".format(phrase)
            
            return results

        #If there were no results in the first place...
        else:
            return "No matches found for search of {0}\n".format(phrase)

    #Search task returns results from call of results function which was given the Mongo search, to the command line interface
    return(results(db.command("text", "entries", search=phrase, filter={"complete": True}, projection={"complete": False})["results"], sort, resultFilter, filterData))

if __name__ == "__main__":
    print("This file only meant for celery tasks. Do not attempt to run it.")
