"""
Created on Jan 25 17:53 2019

@author: garagon
"""
import sys
import logging, os
import json
from src.utils import Utils
import pandas as pd
import pickle

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
class Data_source:

    id_path = "id.config"
    folder_path="config"

    def __init__(self):
        self.util = Utils()


    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        path = self.command_to_execute["host"] + "-" + self.id_path
        self.path = os.path.join(self.folder_path, path)

        for key, value in command_to_execute["data_source"].items():
            if value is not None:
                if key is "list":
                    if len(value) == 1:
                        if "all" in value:
                            #id = self.util.get_id(self.path,"all")
                            self.list(None,"all")
                        elif "ids" in value:
                            self.list(None,"ids")
                        else:
                            id = value
                            self.list(id)
                    else:
                        id = self.util.get_id(self.path, None)
                        self.list(id)

                elif key is "delete":
                    #logger.debug("length "+str(len(value)))
                    if len(value) == 1:
                        if "all" in value:
                            id = self.util.get_id(self.path,"all")
                        else:
                            logger.debug("Value "+str(value))
                            id = value
                    else:
                        id = self.util.get_id(self.path, None)

                    self.delete(id)

                elif key is "add":
                    if len(value) == 2:
                        logger.debug("Value 0 "+str(value[0]))
                        logger.debug("Value 1 " + str(value[1]))
                        self.add(str(value[0]), str(value[1]))
                    else:
                        logger.debug("Value 0 " + str(value[0]))
                        self.add(str(value[0]))


    def list(self, id, all=None):
        #need to use host
        # curl may not work on windows terminal
        logger.debug("list inputs")
        #logger.debug("id list "+str(id))
        if id is not None:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            if isinstance(id,list):
                logger.debug("List of the following instances: "+str(id))
                id_list=self.util.get_id_list(id)
                logger.debug("id list " + str(id_list))
                for element_id in id_list:
                    endpoint = "v1/inputs/dataset/" + element_id
                    response = self.connection.send_request("GET", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))

                    endpoint = "v1/inputs/mqtt/" + element_id
                    response = self.connection.send_request("GET", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))


        elif "all" in all:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            endpoint = "v1/inputs/dataset"
            response = self.connection.send_request("GET", endpoint, payload, headers)
            logger.debug(json.dumps(response, indent=4, sort_keys=True))

            endpoint = "v1/inputs/mqtt"
            response = self.connection.send_request("GET", endpoint, payload, headers)
            logger.debug(json.dumps(response, indent=4, sort_keys=True))

        elif "ids" in all:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }
            endpoint = "v1/inputs/dataset/ids"
            response = self.connection.send_request("GET", endpoint, payload, headers)
            #logger.debug(json.dumps(response, indent=4, sort_keys=True))
            return response
        else:
            logger.error("No ids to list")
            sys.exit(0)

    def delete(self, id):
        #logger.debug("Delete input "+str(id))
        if id is not None:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            if isinstance(id,list):
                try:
                    logger.debug("List of the following instances: "+str(id))
                    id_list = self.util.get_id_list(id)
                    logger.debug("id list to erase " + str(id_list))
                    for self.element_to_erase in id_list:

                        logger.debug("element to erase "+str(self.element_to_erase) + " type "+str(type(self.element_to_erase)))
                        #self.element_to_erase =element
                        path = self.command_to_execute["host"] + "-" + self.id_path
                        path = os.path.join(self.folder_path, path)

                        endpoint = "v1/inputs/dataset/" + self.element_to_erase
                        response = self.connection.send_request("DELETE", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))
                        self.util.erase_id(path,self.element_to_erase)

                        if not "success" in response:
                            endpoint = "v1/inputs/mqtt/" + self.element_to_erase
                            response = self.connection.send_request("DELETE", endpoint, payload, headers)
                            logger.debug(json.dumps(response, indent=4, sort_keys=True))
                            self.util.erase_id(path, self.element_to_erase)


                except Exception as e:
                    path = self.command_to_execute["host"] + "-" + self.id_path
                    path = os.path.join(self.folder_path, path)
                    self.util.erase_id(path,self.element_to_erase)
                    logger.error(e)

        else:
            logger.error("No ids to delete")
            sys.exit(0)


    def add(self, filepath, id=None, instance_name=None, model_name=None):
        logger.debug("Add inputs")

        # collects all ids from ofw if the file is not present
        path = self.command_to_execute["host"] + "-" + self.id_path
        path = os.path.join(self.folder_path, path)
        self.util.collect_store_ids_from_ofw(path)


        #normal working
        payload=""
        try:
            with open(filepath,"r") as myfile:
                payload=myfile.read()
        except Exception as e:
            logger.debug("File path not existing")
            logger.error(e)
            sys.exit(0)

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        #if id was present PUT
        if id is not None:
            #logger.debug("id found for data_source add")
            #logger.debug("id "+id)
            if "mqtt" in payload:
                #logger.debug("mqtt with id")
                endpoint = "v1/inputs/mqtt/"+str(id)
                response=self.connection.send_request("PUT", endpoint, payload, headers)
                logger.debug(json.dumps(response, indent=4, sort_keys=True))
            else:
                #logger.debug("dataset with id")
                endpoint = "v1/inputs/dataset/"+str(id)
                response=self.connection.send_request("PUT", endpoint, payload, headers)
                logger.debug(json.dumps(response, indent=4, sort_keys=True))
        #if no id present POST
        else:
            if "mqtt" in payload:
                #logger.debug("mqtt")
                endpoint = "v1/inputs/mqtt"

            else:
                #logger.debug("file")
                endpoint = "v1/inputs/dataset"

            try:
                response = self.connection.send_request_add("POST", endpoint, payload, headers)
                if response is not None:
                    logger.debug("Id: " + json.dumps(response, indent=4, sort_keys=True))
                    folder="config"
                    path = self.command_to_execute["host"] + "-" + self.id_path
                    path=os.path.join(folder,path)
                    data = {}
                    data[str(model_name)]= [{str(instance_name) : response}]
                    #logger.debug("data "+str(data))
                    #df=pd.DataFrame(data)
                    self.util.store(path,[data])

                    #self.util.store(path)
            except Exception as e:
                logger.error(e)
                sys.exit(0)
