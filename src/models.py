"""
Created on Jan 25 17:53 2019

@author: nishit
"""

import os
import logging, os
import ntpath
import re
import json

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Models:

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        for key, value in command_to_execute["model"].items():
            if value is not None:
                if key is "list":
                    self.list()
                elif key is "delete":
                    self.delete(value)
                elif key is "add":
                    if len(value) == 2:
                        self.add(str(value[0]),str(value[1]))
                    else:
                        filename=self.path_leaf(str(value[0]))
                        self.add(str(value[0]), filename)


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


    def add(self, filepath,model_name ):
        logger.debug("Add")

        try:
            payload=""
            with open(filepath,"r") as myfile:
                payload=myfile.read()

            headers = {
                'cache-control': "no-cache"
            }

            model_name=re.sub("\.(.*)","",model_name)

            endpoint = "v1/models/" + model_name
            logger.debug("model_name: "+str(model_name))
            response=self.connection.send_request("PUT", endpoint, payload, headers)
            logger.debug(json.dumps(response, indent=4, sort_keys=True))
        except Exception as e:
            logger.error(e)

