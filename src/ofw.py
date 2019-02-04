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
import optparse
import logging, os



logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)



def vararg_callback_1(option, opt_str, value, parser):
    assert value is None
    value = []

    def floatable(str):
        try:
            float(str)
            return True
        except ValueError:
            return False
    counter=0
    for arg in parser.rargs:
        # stop on --foo like options
        if arg[:2] == "--" and len(arg) > 2:
            break
        # stop on -a, but not on -3 or -3.0
        if arg[:1] == "-" and len(arg) > 1 and not floatable(arg):
            break

        if counter > 0:
            logger.error("Too many parameters for stop")
            sys.exit(0)
        counter += 1
        value.append(arg)

    del parser.rargs[:len(value)]
    setattr(parser.values, option.dest, value)

def vararg_callback(option, opt_str, value, parser):
    assert value is None
    value = []

    def floatable(str):
        try:
            float(str)
            return True
        except ValueError:
            return False
    counter=0
    for arg in parser.rargs:
        # stop on --foo like options
        if arg[:2] == "--" and len(arg) > 2:
            break
        # stop on -a, but not on -3 or -3.0
        if arg[:1] == "-" and len(arg) > 1 and not floatable(arg):
            break

        if counter > 1:
            logger.error("Too many options for add")
            sys.exit(0)
        counter += 1
        value.append(arg)

    del parser.rargs[:len(value)]
    setattr(parser.values, option.dest, value)

def parser():
    desc = """OFW is an optimization framework that maps inputs and outputs to an optimization model written in pyomo.\t\t\t\t\t\t
    [1]Start registering a new model. If the model is already available in ofw, you don't have to repeat this step. \t\t\t\t\t\t
    [2]Second, register your inputs to create an instance. \t\t\t\t\t\t
    [3]After that you can register your outputs and start/stop ofw"""
    command_to_execute = {}
    parser = optparse.OptionParser(usage='Usage: %prog <options> <endpoint> arg1 arg2', version="%prog 1.0", description=desc)
    parser.add_option('-H', '--host', dest="Host", type="string", help="http host to connect to. Mandatory option.",
                      metavar='<target host>', action="store")
    parser.add_option('-P', '--port', dest="Port", type="string", help="Network port to connect to. Default 8080",
                      metavar='<target port>', action="store")


    ###defining groups and adding data to them
    #######################################################################################
    ###################     command             ############################################
    command_group = optparse.OptionGroup(parser, "Endpoint command")

    command_group.add_option("--start", help="<filepath> <id>   starts the optimnization. If id is not present takes the last id used. Write all to start all instances", dest="start", metavar='<filepath> <id>',
                             action="callback",callback=vararg_callback)
    # command_group.add_option("--start",help="starts the optimnization",dest="start",metavar='<filepath> <id>', nargs=2, action="store")
    command_group.add_option("--stop", help="<id>  stops the optimnization with a given id. If id is not present takes the last id used. Write all to stop all instances", dest="stop",
                             metavar='<id>', action="callback", callback=vararg_callback_1)
    command_group.add_option("--status", help="receives the status of the optimnization", dest="status", action="store_true")

    #######################################################################################
    ###################     INPUT              ############################################

    data_source_group = optparse.OptionGroup(parser, "Endpoint input")

    data_source_group.add_option("--input_add", help="<filepath> <id>   registers a data source. If id is not present takes the last id used. The first time you don't need to enter any id", dest="ds_add",
                                 metavar='<filepath> <id>', action="callback", callback=vararg_callback)
    # data_source_group.add_option("--data_source add", help="registry a data source", dest="ds_add", metavar='<filepath> <id>', nargs=2, action="store")
    data_source_group.add_option("--input_list", help="<id>   gets the registry with the respective id. If id is not present takes the last id used. Write all to have a list of all registered inputs", dest="ds_list",
                                 metavar='<id>', action="callback", callback=vararg_callback_1)
    data_source_group.add_option("--input_delete", help="<id>   deletes the registry with the respective id. If id is not present takes the last id used. Write all to delete all registered inputs", dest="ds_delete",
                                 metavar='<id>', action="callback", callback=vararg_callback_1)

    #######################################################################################
    ###################     OUTPUT              ############################################
    data_output_group = optparse.OptionGroup(parser, "Endpoint output")

    data_output_group.add_option("--output_add", help="<filepath> <id>   registers a data output. If id is not present takes the last id used", dest="do_add",
                                 metavar='<filepath> <id>', action="callback", callback=vararg_callback)
    # data_output_group.add_option("--data_output add", help="registry a data output", dest="do_add",metavar='<filepath> <id>', nargs=2, action="store")
    data_output_group.add_option("--output_list", help="<id>   gets the registry with the respective id. If id is not present takes the last id used. Write all to have a list of all registered outputs", dest="do_list",
                                 metavar='<id>', action="callback", callback=vararg_callback_1)
    data_output_group.add_option("--output_delete", help="<id>   deletes the registry with the respective id. If id is not present takes the last id used.  Write all to delete all registered outputs",
                                 dest="do_delete", metavar='<id>', action="callback", callback=vararg_callback_1)

    #######################################################################################
    ###################     MODEL              ############################################
    models_group = optparse.OptionGroup(parser, "Endpoint model")

    models_group.add_option("--model_add", help="<filepath> <model_name>  registers an optimization model", dest="model_add",
                            metavar='<filepath> <model_name>', action="callback", callback=vararg_callback)
    models_group.add_option("--model_list", help="gets the models name stored at ofw", dest="model_list", action="store_true")
    models_group.add_option("--model_delete", help="deletes an optimization model with the respective id",
                            dest="model_delete", metavar='<model_name>', action="store")

    parser.add_option_group(models_group)
    parser.add_option_group(data_source_group)
    parser.add_option_group(data_output_group)
    parser.add_option_group(command_group)

    (opts, args) = parser.parse_args()

    #variable assignment
    tgtHost = opts.Host
    tgtPort = opts.Port
    #id=opts.id

    model = {"add":opts.model_add, "list": opts.model_list, "delete": opts.model_delete}
    data_source = {"add":opts.ds_add, "list": opts.ds_list, "delete": opts.ds_delete}
    data_output = {"add": opts.do_add, "list": opts.do_list, "delete": opts.do_delete}
    command={"start":opts.start, "stop":opts.stop, "status":opts.status}

    if (tgtHost == None):
        logger.error(parser.usage)
        sys.exit(0)
    elif (tgtPort == None):
        tgtPort = "8080"

    command_to_execute["host"] = tgtHost
    command_to_execute["port"] = tgtPort
    command_to_execute["model"]= model
    command_to_execute["data_source"] = data_source
    command_to_execute["data_output"] = data_output
    command_to_execute["command"] = command

    return command_to_execute


if __name__ == '__main__':
    """
        format:
        api_category command_name required args 
        eg:
        data_source -add file_path      - for post
        data_source -add file_path id   - for put
    """

    command_to_execute = {}
    command_to_execute=parser()

    logger.debug("command to execute: "+str(command_to_execute))
    http = Http(command_to_execute)
    for key, value in command_to_execute["model"].items():
        if value is not None:
            logger.debug("key exists "+str(key))
            logger.debug("Executing the command model")
            model = Models()
            model.execute(http, command_to_execute)

    for key, value in command_to_execute["data_source"].items():
        if value is not None:
            logger.debug("key exists "+str(key))
            logger.debug("Executing the command input")
            data_source = Data_source()
            data_source.execute(http, command_to_execute)

    for key, value in command_to_execute["data_output"].items():
        if value is not None:
            logger.debug("key exists "+str(key))
            logger.debug("Executing the command output")
            data_output = Data_output()
            data_output.execute(http, command_to_execute)

    for key, value in command_to_execute["command"].items():
        if value is not None:
            logger.debug("key exists "+str(key))
            logger.debug("Executing the command")
            command = Command()
            command.execute(http, command_to_execute)
