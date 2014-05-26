#Command line interface for the whole indexing and searching utility

from lib.tasks import index as _index

from lib.tasks import search as _search

#Message printed out by the help command
helpInfo  = "\nAvailable commands:\n\n"
helpInfo += "  INDEX path [title] [+tags]: Adds file in the path to the list of searchable\n"
helpInfo += "                              files with a title and a number of\n"
helpInfo += "                              descriptor tags optional\n"
helpInfo += "  SEARCH phrase             : Searches for occurences of the phrase(s) in all\n"
helpInfo += "                              indexed files and prints out occurences.\n"
helpInfo += "         [-s relevance]     - (Default) Sorts results based on search ranking.\n"
helpInfo += "         [-s date new/old]  - Sort results based on the date they were indexed,\n"
helpInfo += "                              newest first or oldest first.\n"
helpInfo += "         [-f type [+ext.]]  - Filter results to only return files with\n"
helpInfo += "                              the given extension(s).\n"
helpInfo += "  HELP                      : Gives info on commands.\n"
helpInfo += "  *All file paths should use forward slashes (/)"

#Message printed out by a faulty search command.
badExpression = "Improper search expression. Defaulting to only search phrase."

#When a command that doesn't exist is called...
def unrecognizedCommand (command):
    raise ValueError('Command "{0}" not recognized. Use --help for information on commands.'.format(command))

'''Passed all of the initial command line arguments
   Calls the passes info in calls to index and search
   Can be used as an API'''
def run (args):
    #If only "python indexsearch.py"
    if len(args) == 1:
        command = input("Please enter a command. Use the help command for info on commands.\nCommand: ")

        args = command.split(" ")

        if args[0] == "help" or args[0] == "HELP":
            print(helpInfo)

        elif args[0] == "index" or args[0] == "INDEX":
            index(args[1:])

        elif args[0] == "search" or args[0] == "SEARCH":
            search(args[1:])

        else:
            #If it's not one of the three available commands
            unrecognizedCommand(args[0])

    elif len(args) > 1:
        if args[1] == "--help" or args[1] == "help" or args[1] == "HELP":
            print(helpInfo)

        elif args[1] == "index" or args[1] == "INDEX":
            index(args[2:])

        elif args[1] == "search" or args[1] == "SEARCH":
            search(args[2:])

        else:
            #If it's not one of the three available commands
            unrecognizedCommand(args[1])

#Starts an _index task and lets it loose
def index (args):
    if len(args) == 0:
        index(input("Please enter path of file and optional information -> path [title] [+tags]...:\n").split(" "))

    elif len(args) > 0:
        #If there are no tags then an empty list is sent, but can't use index for title if there isn't args[1]
        _index.delay(args[0], {"title": "" if len(args) == 1 else args[1], "tags": args[2:]})

#Starts a _search task and prints out the results
def search (args):
    #A lot of flow control for different possible commands and protecting against people doing them incorrectly.
    if len(args) == 0:
        search(input("Please enter phrase to search (for sorts and filters see help command):\n").split(" "))

    #Starts a _search task and gets the result
    elif len(args) >= 1:
        if len(args) == 1:
            results = _search.delay(args[0]).get()

        elif len(args) >= 3:
            if args[1] == "-s":
                if args[2] == "relevance":
                    results = _search.delay(args[0]).get()

                elif args[2] == "date":
                    if len(args) == 4:
                        if args[3] == "new":
                            results = _search.delay(args[0], sort="date-new").get()

                        elif args[3] == "old":
                            results = _search.delay(args[0], sort="date-old").get()

                        else:
                            print(badExpression)

                            results = _search.delay(args[0]).get()
                    else:
                        print(badExpression)

                        results = _search.delay(args[0]).get()

                else:
                    print(badExpression)

                    results = _search.delay(args[0]).get()

            elif args[1] == "-f":
                if args[2] == "type" and len(args) >= 4:
                    results = _search.delay(args[0], resultFilter="type", filterData=args[3:]).get()

                else:
                    print(badExpression)
                    
                    results = _search.delay(args[0]).get()
                
            else:
                print(badExpression)

                results = _search.delay(args[0]).get()

        else:
            print(badExpression)

            results = _search.delay(args[0]).get()
        
        #Handling the results
        print("\n")

        #If it's just sending the string saying that there were no results...
        if not type(results) is list and type(results) is str:
            print(results)

            return

        #If there's less than or five results, print all of them
        if len(results) <= 5:
            for result in results:
                print(result)

        #For more than 5, print out 5 and ask if they want the rest.
        else:
            for i in range(5):
                print(results[i])

                if i >= 4 and len(results) > 5:
                    show = input("More results are hidden. Show them? (Y/N): ")

                    #If they say Y... 
                    if show == "Y":
                        for j in range(i + 1, len(results)):
                            print(results[j])

                    #If they say anything other than Y...


if __name__ == "__main__":
    from sys import argv

    #Pass arguments on to run to handle
    run(argv)
