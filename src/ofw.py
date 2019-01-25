"""
Created on Jan 25 16:42 2019

@author: nishit
"""
import sys

from src.models import Models

"""
~$variable = that variable is not necessary. if present than put api, otherwise post api 
"""

api_category = {"command": {"start":"filepath,id", "stop":"id"}
, "data_source":{"add": {"file":"filepath,~id", "mqtt":"filepath,~id"}, "delete": {"file":"id", "mqtt":"id", "all":""}}
, "data_output": {"add":"filepath", "get":"id"}
, "models": {"add":"modelname,filepath","delete":{"modelname":"", "all":""}, "list":""}}


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
        data_source file file_path      - for post
        data_source file file_path id   - for put
    """
    number_of_args = len(sys.argv)
    if number_of_args < 2:
        print("please enter a command and args in the command line\n"
              "ofw.exe data_source file $file_path")
        sys.exit(0)
    command_to_execute = {}
    category = sys.argv[1]
    if category not in api_category.keys():
        print("Please enter one of the following command categories: " + str(api_category.keys()))
        sys.exit(0)
    else:
        command_to_execute["category"] = category
        command_name = sys.argv[2]
        if command_name not in api_category[category].keys():
            print("Please enter one of the following commands: " + str(api_category[category].keys()))
            sys.exit(0)
        else:
            command_to_execute["command"] = command_name
            command_dict = api_category[category][command_name]
            if number_of_args > 3:
                command_line_value = sys.argv[3]
                if isinstance(command_dict, dict):
                    if command_line_value in command_dict.keys():
                        command_to_execute[command_name] = command_line_value
                        value = command_dict[command_line_value]
                        if isinstance(value, str) and len(value) > 0:
                            split_and_add_args(4)
                    else:
                        print("incorrect values")
                elif isinstance(command_dict, str):
                    value = command_dict
                    if isinstance(value, str) and len(value) > 0:
                        split_and_add_args(3)

    print(command_to_execute)
    if command_to_execute["category"] == "models":
        Models.execute(command_to_execute, None)
