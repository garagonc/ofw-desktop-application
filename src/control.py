"""
Created on Jan 25 17:53 2019

@author: garagon
"""
import sys
import logging, os
import json
import csv
import pandas as pd
from src.utils import Utils
#import xlsxwriter

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
class Data_output:

    id_path="id.config"
    output_path= "output.csv"

    def __init__(self):
        self.util=Utils()


    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute
        folder = "config"
        path = self.command_to_execute["host"] + "-" + self.id_path
        self.path = os.path.join(folder, path)

        for key, value in command_to_execute["data_output"].items():
            if value is not None:
                if key is "list":
                    if len(value) == 1:
                        if "all" in value:
                            id = self.util.get_id(self.path,"all")
                        else:
                            id = value
                    else:
                        id = self.util.get_id(self.path, None)
                    self.list(id)

                elif key is "delete":
                    if len(value) == 1:
                        if "all" in value:
                            id = self.util.get_id(self.path,"all")
                        else:
                            id = value
                    else:
                        id = self.util.get_id(self.path, None)

                    self.delete(id)

                elif key is "add":
                    if len(value) == 2:
                        self.add(str(value[0]), str(value[1]))
                    else:
                        id=self.util.get_id(self.path, None)
                        if id is not None:
                            self.add(str(value[0]), id)
                        else:
                            self.add(str(value[0]))


    def list(self, id):
        if id is not None:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            if isinstance(id,list):
                logger.debug("List of the following instances: "+str(id))
                id_list = self.util.get_id_list(id)
                logger.debug("id list " + str(id_list))
                for element_id in id_list:
                    endpoint = "v1/outputs/" + element_id
                    response = self.connection.send_request("GET", endpoint, payload, headers)
                    df = pd.DataFrame(response)
                    logger.debug(df)
                    #logger.debug(json.dumps(response, indent=4, sort_keys=True))
                    folder = "outputs"
                    name = "output-" + str(element_id) + ".xlsx"
                    path = os.path.join(folder, name)
                    msg=self.util.store_as_excel(path, df, id)
                    logger.debug(msg)
        else:
            logger.error("No ids to list")
            sys.exit(0)


    def delete(self, id):
        logger.debug("Delete data_output "+str(id))
        if id is not None:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }


            if isinstance(id,list):
                logger.debug("List of the following instances: "+str(id))
                id_list = self.util.get_id_list(id)
                logger.debug("id list " + str(id_list))
                for self.element_to_erase in id_list:

                    endpoint = "v1/outputs/mqtt/" + self.element_to_erase
                    response = self.connection.send_request("DELETE", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))


                    if not "success" in response:
                        endpoint = "v1/outputs/" + self.element_to_erase
                        response = self.connection.send_request("DELETE", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))

        else:
            logger.error("No ids to delete")
            sys.exit(0)

    def add(self, filepath, id=None, connection=None):
        logger.debug("Add data_output")

        if connection is not None:
            self.connection=connection
            flag_instance=True

        if not isinstance(filepath, dict):
            try:
                with open(filepath, "r") as myfile:
                    payload = myfile.read()
            except Exception as e:
                logger.debug("File path not existing")
                logger.error(e)
                sys.exit(0)
        else:
            payload = json.dumps(filepath)


        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }
        logger.debug("id "+str(id))
        if isinstance(id, list):
            logger.debug("List of the following instances: " + str(id))
            for element in id:
                logger.debug("List of "+str(element))
                for model_name in element.keys():
                    for list_2 in element[model_name]:
                        for instance_name in list_2.keys():
                            self.id_to_add = list_2[instance_name]
                logger.debug("id to add"+str(self.id_to_add))
                endpoint = "v1/outputs/mqtt/"+self.id_to_add
                response=self.connection.send_request("PUT", endpoint, payload, headers)
                logger.debug(json.dumps(response, indent=4, sort_keys=True))
        else:
            logger.error("Id is missing as parameter")
            sys.exit(0)

