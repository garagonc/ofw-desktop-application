"""
Created on Jan 25 17:53 2019

@author: nishit
"""

import os
import logging, os, sys
import ntpath
import re
import json
import pandas
from src.models import Models
from src.data_source import Data_source
from src.utils import Utils
import pandas as pd

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Instance:

    id_path="id.config"
    folder_path="config"

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def __init__(self):
        self.util = Utils()

    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        #df=pandas.read_csv("Table_format.xlsx")
        #logger.debug(df)



        for key, value in command_to_execute["instance"].items():
            if value is not None:
                if key is "list":
                    self.list(value)
                elif key is "delete":
                    if len(value) == 2:
                        self.delete(str(value[0]),str(value[1]))
                    elif len(value) == 1:
                        self.delete(str(value[0]), None)
                    elif len(value) == 0:
                        self.delete(None, None)
                    else:
                        logger.debug("Entered more values than supported")
                        sys.exit(0)

                elif key is "add":
                    if len(value) == 2:
                        self.add(str(value[0]),str(value[1]))

    def list(self, model_name_input=None):
        if model_name_input is not None:
            if "all"in model_name_input:
                #get all model_names and instances
                folder = "instances"
                folder_path = os.path.join(folder)
                model_names=self.util.get_all_folder_names(folder)
                #logger.debug("model names "+str(model_names))
                dict = {}
                dict1={}
                for model in model_names:
                    folder = "instances"
                    folder_path = os.path.join(folder, model)
                    instance_names = self.util.get_all_files_from_folder(folder_path)
                    #logger.debug("instance names " + str(instance_names))
                    dict[model] = instance_names
                dict1["instance_list"] = dict
                #logger.debug("dict1 " + str(dict1))
                df = pd.DataFrame(dict1)
                logger.debug(df)
            else:
                #get instances for one model_name
                folder = "instances"
                folder_path = os.path.join(folder, model_name_input)
                instance_names = self.util.get_all_files_from_folder(folder_path)
                #logger.debug("instance names " + str(instance_names))
                dict={}
                dict1={}
                dict[model_name_input]=instance_names
                dict1["instance_list"]=dict
                #logger.debug("dict1 " + str(dict1))
                df = pd.DataFrame(dict1)
                logger.debug(df)
        else:
            logger.error("Enter a model name")
            sys.exit(0)


    def delete(self, model_name_input=None,instance_name_input=None):
        logger.debug("Delete")
        #logger.debug("model name "+str(model_name_input))
        #logger.debug("instace_name "+str(instance_name_input))

        path = self.command_to_execute["host"] + "-" + self.id_path
        path = os.path.join(self.folder_path, path)

        self.input_object=Data_source()

        if model_name_input is not None:

            #two possibilities: 1 existing model_name 2. "all"
            if "all" in model_name_input:
                logger.debug("Erase all model name instances")
                id = self.util.get_id(path, None, model_name_input, instance_name_input)
                id_list = self.util.get_id_list(id)
                logger.debug("id " + str(id_list))
                self.input_object.delete(id_list, path, self.connection)
                folder = "instances"
                self.util.delete_all_files_from_folder(folder)
                instance_folder_path = os.path.join(folder, model_name_input)
                if self.util.is_dir_empty(instance_folder_path):
                    self.util.delete_folder(instance_folder_path)

            else:
                if instance_name_input is not None:
                    if "all" in instance_name_input:
                        logger.debug("Erasing all instances")
                        id = self.util.get_id(path, None, model_name_input, instance_name_input)
                        id_list = self.util.get_id_list(id)
                        logger.debug("id " + str(id_list))
                        self.input_object.delete(id_list, path, self.connection)
                        folder = "instances"
                        instance_folder_path = os.path.join(folder, model_name_input)
                        self.util.delete_all_files_from_folder(instance_folder_path)
                        if self.util.is_dir_empty(instance_folder_path):
                            self.util.delete_folder(instance_folder_path)
                    else:
                        logger.debug("Erasing instance "+str(instance_name_input))
                        id=self.util.get_id(path,None,model_name_input,instance_name_input)
                        id_list = self.util.get_id_list(id)
                        logger.debug("id "+str(id_list))
                        self.input_object.delete(id_list, path, self.connection)
                        folder = "instances"
                        instance_path = os.path.join(folder, model_name_input, instance_name_input) + ".xlsx"
                        #instance_path =self.util.get_path(instance_path)
                        self.util.deleteFile(instance_path)
                        folder_path= os.path.join(folder, model_name_input)
                        if self.util.is_dir_empty(folder_path):
                            self.util.delete_folder(folder_path)

                else:
                    logger.debug("Erasing last instance used")
                    id = self.util.get_id(path, None, model_name_input, instance_name_input)
                    id_list = self.util.get_id_list(id)
                    logger.debug("id " + str(id_list))
                    self.input_object.delete(id_list, path, self.connection)
                    instance_name_input = self.util.get_instance_name(id)
                    folder = "instances"
                    instance_path = os.path.join(folder, model_name_input, instance_name_input) + ".xlsx"
                    #instance_path = self.util.get_path(instance_path)
                    self.util.deleteFile(instance_path)
                    folder_path = os.path.join(folder, model_name_input)
                    if self.util.is_dir_empty(folder_path):
                        self.util.delete_folder(folder_path)

            logger.debug("Erase completed successfully")
        else:
            logger.error("Model_name is missing")
            sys.exit(0)



    def add(self,model_name,instance_name):

        logger.debug("Adding an instance")
        #logger.debug("Instance name "+str(instance_name))
        #logger.debug("Model name "+str(model_name))
        folder = "instances"
        folder_path = os.path.join(folder, model_name)
        path = os.path.join(folder, model_name, instance_name) + ".xlsx"
        path=self.util.get_path(path)
        # logger.debug("path "+str(path))
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            #Call a function that reads the input, outputs from model_name and start parameters
            data=self.readInputsOutputs(model_name)
            #Call a function that inserts the inputs and output information and generates a muster instance_name.xlsx
            #logger.debug("data "+str(data))
            self.util.generate_xlsx_instance_config(data,path)
            logger.debug("File "+str(path)+" created")
        except Exception as e:
            logger.error(e)

    def readInputsOutputs(self, model_name):
        logger.debug("Reading inputs and outputs from optimization model "+str(model_name))
        models = Models()
        data = models.list(model_name,self.connection)
        data=data.decode("utf-8")
        data_set = [x for x in data.split("\n") if "Set" in x]
        data_param_1 = []
        for item in data_set:
            #logger.debug("item param " + str(item))
            item = re.sub("=(.*)", "", item)
            item = re.sub("model.", "", item)
            item = re.sub("\s+\Z", "", item)
            #logger.debug("item param " + str(item) + " type "+str(type(item)))
            if not "#" in item and item != "T":
                #logger.debug("item param " + str(item))
                data_param_1.append(item)
        #logger.debug("data param "+str(data_param_1))
        data_param = [x for x in data.split("\n") if "Param" in x]
        #data_param_1=[]
        for item in data_param:
            #logger.debug("item param "+str(item)
            item = re.sub("=(.*)", "", item)
            item = re.sub("model.", "", item)
            item = re.sub("\s+\Z", "", item)
            if not "#" in item and item != "dT":
                data_param_1.append(item)
        #logger.debug("data param " + str(data_param_1))
        data_var = [x for x in data.split("\n") if "Var" in x]
        data_var_1=[]
        for item in data_var:
            item = re.sub("=(.*)", "", item)
            item = re.sub("model.", "", item)
            item = re.sub("\s+\Z", "", item)
            if not "#" in item:
                data_var_1.append(item)

        start=["control_frequency","horizon_in_steps","dT_in_seconds","repetition", "optimization_type","solver"]
        data_to_return={}
        data_to_return["inputs"] = data_param_1
        data_to_return["outputs"] = data_var_1
        data_to_return["start"] = start
        #logger.debug("data to return " + str(data_to_return))
        return data_to_return

