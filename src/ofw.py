"""
Created on Jan 25 16:42 2019

@author: nishit
"""
import sys

from src.models import Models
from src.data_source import Data_source
from src.control import Data_output
from src.command import Command
from src.http import Http
from src.help import Help
import optparse

"""
~$variable = that variable is not necessary. if present than put api, otherwise post api 
"""
other_commands={"-host":"hostname","-port":"port"}

api_category = {"command": {"-start":"filepath,id", "-stop":"id", "-status":""}
, "data_source":{"-add":"filepath,~id", "-delete": "~id", "-list":""}
, "data_output": {"-add":"filepath,~id", "-list":"id"}
, "models": {"-add":"filepath,model_name","-delete":"~model_name", "-list":""}}

commands={"add", "delete", "list", "start", "stop"}



def split_and_add_args(index):
    global args, i, v, arg
    args = value.split(",")
    for i in range(len(args)):
        v = args[i]
        if "~" not in v and index + i >= number_of_args:
            print("incomplete data " + str(v) + " not present")
            sys.exit(0)
        if "~" in v:
            v = v[1:]
        if index + i < number_of_args:
            arg = sys.argv[index + i]
            command_to_execute[v] = arg



if __name__ == '__main__':
    """
        format:
        api_category command_name required args 
        eg:
        data_source -add file_path      - for post
        data_source -add file_path id   - for put
    """
    number_of_args = len(sys.argv)
    print("number of args: "+str(len(sys.argv)))
    if number_of_args < 2:
        print("please enter a command and args in the command line. Example:\n"
              "ofw.exe data_source -add file $file_path")
        sys.exit(0)
    command_to_execute = {}

    #check the position of the host and port name
    counter = 0
    help = False
    category_position_host = 0
    category_position_port = 0

    #checking if the --help option was used
    for name in sys.argv:
        if "--help" in name:
            help=True
            break
        for key in other_commands.keys():
            if key in name:
                command_to_execute[key]=sys.argv[counter + 1]
        counter += 1

    if help:
        Help.help_text()
        sys.exit(0)

    for key in other_commands.keys():
        if not command_to_execute[key]:
            print("No "+str(key)+" present.\n"
                "try 'ofw --help' for more information")
            sys.exit(0)

    #Decoding the commands
    counter=0
    category_position=1
    for name in sys.argv:
        if name in api_category.keys():
            category_position=counter
        counter += 1

    category = sys.argv[category_position]
    print("category: " + str(sys.argv[category_position]))
    if category not in api_category.keys():
        print("Please enter the following command categories: " + str(api_category.keys()))
        sys.exit(0)
    else:
        command_to_execute["category"] = category
        command_name = sys.argv[category_position+1]
        print("command_name: " + str(sys.argv[category_position+1]))
        if command_name not in api_category[category].keys():
            print("Please enter one of the following commands: " + str(api_category[category].keys()))
            sys.exit(0)
        else:
            command_to_execute["command"] = command_name
            command_dict = api_category[category][command_name]
            print("number of args: "+str(number_of_args))
            print("category position: " + str(category_position))
            if number_of_args > category_position+2:
                command_line_value = sys.argv[category_position+2]
                print("command_line_value: " + str(command_line_value))
                print("command_dict: " + str(api_category[category][command_name]))
                #command_to_execute[command_name] = command_line_value
                value = command_dict
                print("value " + str(type(command_dict)))
                if isinstance(value, str) and len(value) > 0:
                    split_and_add_args(category_position + 2)
            else:
                if command_to_execute["command"] == "-list":
                    print("list")
                else:
                    print("incorrect values")
                    print("Please enter the following commands: " + str(api_category[category][command_name]))
                    sys.exit(0)

    print(command_to_execute)
    http=Http(command_to_execute)
    if command_to_execute["category"] == "models":
        print("Executing the command")
        model=Models()
        model.execute(http, command_to_execute)
    elif command_to_execute["category"] == "data_source":
        print("Executing the command")
        data_source=Data_source()
        data_source.execute(http, command_to_execute)
    elif command_to_execute["category"] == "data_output":
        print("Executing the command")
        data_output=Data_output()
        data_output.execute(http, command_to_execute)
    elif command_to_execute["category"] == "command":
        print("Executing the command")
        command=Command()
        command.execute(http, command_to_execute)

