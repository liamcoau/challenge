from lib.tasks import index as _index
from lib.tasks import search as _search

helpInfo  = "\nAvailable commands:\n\n"
helpInfo += "  INDEX path [+ path]...     : Adds file(s) in the path(s) to the list of\n"
helpInfo += "                               searchable files.\n"
helpInfo += "  SEARCH phrase [+ phrase]...: Searches for occurences of the phrase(s) in all\n"
helpInfo += "                               indexed files and prints out occurences.\n"
helpInfo += "  HELP                       : Gives info on commands."

def unrecognizedCommand (command):
    raise ValueError('Command "{0}" not recognized. Use --help for information on commands.'.format(command))

def run (args):
    if len(args) == 1:
        command = input("Please enter a command. Use the help command for info on commands.\nCommand: ")
        print(command)
        args = command.split(" ")
        if args[0] == "help":
            print(helpInfo)
        elif args[0] == "index":
            index(args[1:])
        elif args[0] == "search":
            search(args[1:])
        else:
            unrecognizedCommand(args[0])
    elif len(args) > 1:
        if args[1] == "--help" or args[1] == "help":
            print(helpInfo)
        elif args[1] == "index":
            index(args[2:])
        elif args[1] == "search":
            search(args[2:])
        else:
            unrecognizedCommand(args[1])

def index (args):
    print(args)
    if len(args) == 0:
        index(input("Please enter file(s) to index (multiple files separated by spaces):\n").split(" "))
    elif len(args) >= 1:
        for path in args:
            _index.delay(path)

def search (args):
    print(args)

if __name__ == "__main__":
    from sys import argv
    print(argv)
    run(argv)

