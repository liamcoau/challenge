challenge
=========

Streamlyne Technologies Ltd. Technical Challenge

This allows you to index files then search for a phrase in all of the indexed files and modify results with sorts and filters.
Files you index can be given a title useful for finding them instead of just the name of the file.
You can also tag the files as a way of categorizing them.

Currently supported file types: .txt .json

#####

Available commands:

    INDEX path [title] [+tags]: Adds file in the path to the list of searchable
  
                                files with a title and a number of
                              
                                descriptor tags optional
                              
    SEARCH phrase             : Searches for occurences of the phrase(s) in all
  
                                indexed files and prints out occurences.
                              
           [-s relevance]     - (Default) Sorts results based on search ranking.
         
           [-s date new/old]  - Sort results based on the date they were indexed,
         
                                newest first or oldest first.
                              
           [-f type [+ext.]]  - Filter results to only return files with
         
                                the given extension(s).
                              
    HELP                      : Gives info on commands.
  

Note that all paths should be given using forward slashes, on all platforms.

#####

To install the requirements, navigate to the directory for challenge run "pip install -r requirements.txt"

#####

To use,

In the command line, run "mongod" to start mongodb.

Navigate to the directory for challenge, and run "celery worker --app=lib -l info" in the command line to start the celery task server.

Navigate to the directory for challenge, and from there run "python indexsearch.py [parameters]..." to use the project.

Examples:

```bash
python indexsearch.py index reports/12531.txt "Program is crashing" crash critical bug-report
```

```bash
python indexsearch.py search bug-report -s date new
```

```bash
python indexsearch.py help
```

If you do not enter parameters, or the required parameters for INDEX and SEARCH, indexsearch.py will prompt you for the required information.

#####

The .json feature has a template that must be followed.

Example:

```
{
    "entries": [
        {"title": "Program is crashing",
         "text": "My program keeps crashing and I don't know why blah blah blah",
         "tags": "crash critical bug-report"
        }
    ]
}
```

"entries" is the key corresponding to a list of all of the entries in the file. You can have multiple objects/dictionaries,
where "title" is equivalent to [title], "text" is equivalent to the contents of the file and "tags" is equivalent to [+tags]

```bash
python indexsearch.py index reports/12531.json
```
where the contents of 12531.json is the above example is equivalent to:

```bash
python indexsearch.py index reports/12531.txt "Program is crashing" crash critical bug-report
```
where the contents of 12531.txt is "My program keeps crashing and I don't know why blah blah blah" (without quotes)

This feature is designed to be useful for indexing and searching posts on a website, and free from the command line would accept json objects instead of files.