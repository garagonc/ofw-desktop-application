"""
Created on Jan 25 17:53 2019

@author: nishit
"""

import os
import logging, os
import ntpath
import re
import json
import pandas
from src.models import Models

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Instance:

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        #df=pandas.read_csv("Table_format.xlsx")
        #logger.debug(df)


        for key, value in command_to_execute["instance"].items():
            if value is not None:
                if key is "list":
                    self.list()
                elif key is "delete":
                    self.delete(value)
                elif key is "add":
                    if len(value) == 2:
                        self.add(str(value[0]),str(value[1]))

    def list(self):
        #need to use host
        # curl may not work on windows terminal
        logger.debug("list")
        payload = ""
        headers = {
            'cache-control': "no-cache"
        }
        response=self.connection.send_request("GET","v1/models",payload, headers)
        logger.debug(json.dumps(response, indent=4, sort_keys=True))
        return response


    def delete(self, model_name):
        logger.debug("Delete")
        #model_name=self.command_to_execute["model_name"]
        if "all" in model_name:
            payload = ""
            headers = {
                'cache-control': "no-cache"
            }
            models = self.list()
            logger.debug("model name: " + str(models["models"]))
            for name in models["models"]:
                #logger.debug("model name: "+str(name))
                for key, value in name.items():
                    #logger.debug("value: " + str(value))
                    endpoint = "v1/models/" + value
                    response=self.connection.send_request("DELETE", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))
        else:
            payload = ""
            headers = {
                'cache-control': "no-cache"
            }
            endpoint= "v1/models/" + model_name
            response=self.connection.send_request("DELETE", endpoint, payload, headers)
            logger.debug(json.dumps(response, indent=4, sort_keys=True))
        #if self.command_to_execute[""]


    def add(self, instance_name,model_name):
        logger.debug("Adding an instance")
        logger.debug("Instance name "+str(instance_name))
        logger.debug("Model name "+str(model_name))
        folder="instances"
        filename="instance_name.xlsx"
        folder_path=os.path.join(folder,model_name)
        path = os.path.join(folder,model_name,instance_name)
        logger.debug("path "+str(path))
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            #Call a function that reads the input, outputs from model_name and start parameters
            data=self.readInputsOutputs(model_name)
            #ToDo Call a function that inserts the inputs and output information and generates a muster instance_name.xlsx
            with open(path, 'w') as outfile:
                outfile.write(data)
            logger.debug("File "+str(path)+" created")
        except Exception as e:
            logger.error(e)

    def readInputsOutputs(self, model_name):
        logger.debug("Reading inputs and outputs")
        models = Models()
        data = models.list(model_name,self.connection)
        data=data.decode("utf-8")
        data_param = [x for x in data.split("\n") if "Param" in x]
        data_param_1=[]
        for item in data_param:
            #logger.debug("item param "+str(item))
            if not "dT" in item:
                item = re.sub("=(.*)", "", item)
                item = re.sub("model.", "", item)
                item = re.sub("\s+\Z", "", item)
                if not "#" in item:
                    data_param_1.append(item)

        data_var = [x for x in data.split("\n") if "Var" in x]
        data_var_1=[]
        for item in data_var:
            item = re.sub("=(.*)", "", item)
            item = re.sub("model.", "", item)
            item = re.sub("\s+\Z", "", item)
            if not "#" in item:
                data_var_1.append(item)

        start=["control_frequency","horizon_in_steps","dT_in_seconds","model_name","repetition","solver"]
        data_to_return={}
        data_to_return["inputs"] = data_param_1
        data_to_return["outputs"] = data_var_1
        data_to_return["start"] = start
        #logger.debug("data to return " + str(data_to_return))
        return data_to_return

