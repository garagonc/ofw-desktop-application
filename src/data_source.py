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
from src.control import Data_output

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
class Data_source:

    id_path = "id.config"
    folder_path="config"

    def __init__(self):
        self.util = Utils()
        self.flag =False


    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute
        self.flag = True

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
                        id_list = self.util.get_id_list(id)
                        self.list(id_list)

                elif key is "delete":
                    #logger.debug("length "+str(len(value)))
                    if len(value) == 1:
                        if "all" in value:
                            id_dict = self.util.get_id(self.path,"all")
                            id = self.util.get_id_list(id_dict)
                        else:
                            logger.debug("Value "+str(value))
                            id = value
                    else:
                        id_dict = self.util.get_id(self.path, None)
                        id = self.util.get_id_list(id_dict)

                    self.delete(id)

                elif key is "add":
                    if len(value) == 2:
                        id = [value[1]]
                        self.add(str(value[0]), id)
                    else:
                        #logger.debug("Value 0 " + str(value[0]))
                        self.add(str(value[0]))


    def list(self, id, all=None):
        #need to use host
        # curl may not work on windows terminal
        logger.debug("list inputs")
        logger.debug("id "+str(id))
        payload = ""

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }


        if id is not None:

            if all is None:
                if isinstance(id,list):
                    #logger.debug("List of the following instances: "+str(id))

                    logger.debug("Id list " + str(id))
                    values=[]
                    for element_id in id:
                        endpoint = "v1/inputs/dataset/" + element_id
                        response = self.connection.send_request("GET", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))
                        if len(response) > 0:
                            values.append(response)

                        endpoint = "v1/inputs/mqtt/" + element_id
                        response = self.connection.send_request("GET", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))
                        if len(response) > 0:
                            values.append(response)


                    folder = "inputs"
                    name = "input-" + str(element_id) + ".json"
                    path = os.path.join(folder, name)
                    self.util.store(path, values)
            else:
                logger.error("Value in all not supported")
                sys.exit(0)

        else:
            if "all" in all:

                values = []
                endpoint = "v1/inputs/dataset"
                response = self.connection.send_request("GET", endpoint, payload, headers)
                logger.debug(json.dumps(response, indent=4, sort_keys=True))
                if len(response) > 0:
                    values.append(response)

                endpoint = "v1/inputs/mqtt"
                response = self.connection.send_request("GET", endpoint, payload, headers)
                logger.debug(json.dumps(response, indent=4, sort_keys=True))
                if len(response) > 0:
                    values.append(response)

                # df = pd.DataFrame(values)
                # logger.debug(df)
                # logger.debug(json.dumps(response, indent=4, sort_keys=True))
                folder = "inputs"
                name = "All_inputs" + ".json"
                path = os.path.join(folder, name)
                self.util.store(path, values)
                # msg = self.util.store_as_excel(path, df, id)
                # logger.debug(msg)

            elif "ids" in all:

                endpoint = "v1/inputs/dataset/ids"
                response = self.connection.send_request("GET", endpoint, payload, headers)
                list_to_send = []
                list_to_send = response
                endpoint = "v1/inputs/mqtt/ids"
                response = self.connection.send_request("GET", endpoint, payload, headers)
                for element in response:
                    list_to_send.append(element)
                if self.flag:
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))
                return list_to_send
            else:
                logger.error("Please use \"all\" or \"ids\"")
            #logger.error("No ids to list")


    def delete(self, id, id_path=None, connection=None):
        #logger.debug("Delete input "+str(id))
        if id is not None:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            if connection is not None:
                self.connection = connection

            if isinstance(id,list):
                try:
                    #logger.debug("List of the following instances: "+str(id))
                    #id_list = self.util.get_id_list(id)
                    logger.debug("Id list to erase " + str(id))
                    if id_path is None:
                        path = self.command_to_execute["host"] + "-" + self.id_path
                        path = os.path.join(self.folder_path, path)
                    else:
                        path = id_path
                    self.output_object= Data_output()
                    for self.element_to_erase in id:

                        logger.debug("element to erase "+str(self.element_to_erase))
                        #self.element_to_erase =element
                        endpoint = "v1/outputs/mqtt/" + self.element_to_erase
                        response = self.connection.send_request("DELETE", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))

                        endpoint = "v1/inputs/dataset/" + self.element_to_erase
                        response = self.connection.send_request("DELETE", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))
                        #self.util.erase_id(path,self.element_to_erase)

                        #if not "success" in response:
                        endpoint = "v1/inputs/mqtt/" + self.element_to_erase
                        response = self.connection.send_request("DELETE", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))
                        self.util.erase_id(path, self.element_to_erase)


                except Exception as e:
                    logger.error(e)

        else:
            logger.error("No ids to delete")



    def add(self, filepath, id=None, model_name=None, instance_name=None, id_path=None, connection=None):
        logger.debug("Add inputs")
        logger.debug("id "+str(id) + " type "+str(type(id)))

        if not id_path:
            path = self.command_to_execute["host"] + "-" + self.id_path
            path = os.path.join(self.folder_path, path)
        else:
            path=id_path

        if connection is not None:
            self.connection=connection

        # collects all ids from ofw if the file is not present
        self.collect_store_ids_from_ofw(path)

        #normal working
        if not isinstance(filepath,dict):
            try:
                with open(filepath,"r") as myfile:
                    payload=myfile.read()
            except Exception as e:
                logger.debug("File path not existing")
                logger.error(e)
                sys.exit(0)
        else:
            payload=json.dumps(filepath)

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        #if id was present PUT
        if id is not None:
            #id_list=self.util.get_id_list(id)
            id_list=id
            logger.debug("id_list "+str(id_list))
            for id_element in id_list:
                if "mqtt" in payload:
                    #logger.debug("mqtt with id")
                    endpoint = "v1/inputs/mqtt/"+str(id_element)
                    response=self.connection.send_request("PUT", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))
                else:
                    #logger.debug("dataset with id")
                    endpoint = "v1/inputs/dataset/"+str(id_element)
                    response=self.connection.send_request("PUT", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))
        #if no id present POST
        else:
            if "mqtt" in payload:
                #logger.debug("mqtt")
                endpoint = "v1/inputs/mqtt"

            else:
                logger.debug("file")
                endpoint = "v1/inputs/dataset"

            try:
                response = self.connection.send_request_add("POST", endpoint, payload, headers)
                if response is not None:
                    logger.debug("Id: " + json.dumps(response, indent=4, sort_keys=True))
                    #logger.debug("instance name "+str(instance_name))
                    #logger.debug("model name " + str(model_name))
                    #logger.debug("pyth " + str(path))

                    data=self.util.integrate_id_in_model_name(path,response,model_name,instance_name)
                    #logger.debug("data "+str(data))
                    data_relocated=self.util.relocate_id([response],data,model_name,instance_name)
                    #logger.debug("data relocated "+str(data_relocated))
                    self.util.store(path,data_relocated)

            except Exception as e:
                logger.error(e)
                sys.exit(0)

    def collect_store_ids_from_ofw(self,path):
        if not self.util.isFile(path):
            ids=self.list(None,"ids")
            #logger.debug("ids list "+str(ids))
            if ids is not None:
                ids_to_store = []
                for element in ids:
                    ids_dict = {}
                    ids_dict["None"]=  [{"None": element}]
                    ids_to_store.append(ids_dict)
                #logger.debug("ids_to_store "+str(ids_to_store))
                if len(ids_to_store) > 0:
                    self.util.store(path,ids_to_store)
