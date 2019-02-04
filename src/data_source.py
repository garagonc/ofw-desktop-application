"""
Created on Jan 25 17:53 2019

@author: garagon
"""
import sys
import logging, os
import json


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
class Data_source:

    id_path = "id.config"

    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        for key, value in command_to_execute["data_source"].items():
            if value is not None:
                if key is "list":
                    if len(value) == 1:
                        if "all" in value:
                            id = self.get_id(self.id_path,"all")
                        else:
                            id = value
                    else:
                        id = self.get_id(self.id_path, None)
                    if id is not None:
                        self.list(id)
                    else:
                        self.list(None)
                elif key is "delete":
                    logger.debug("length "+str(len(value)))
                    if len(value) == 1:
                        if "all" in value:
                            id = self.get_id(self.id_path,"all")
                        else:
                            logger.debug("Value "+str(value))
                            id = value
                    else:
                        id = self.get_id(self.id_path, None)
                    if id is not None:
                        logger.debug("id "+str(id))
                        self.delete(id)
                    else:
                        self.delete(None)
                elif key is "add":
                    if len(value) == 2:
                        self.add(str(value[0]), str(value[1]))
                    else:
                        self.add(str(value[0]))


    def list(self, id):
        #need to use host
        # curl may not work on windows terminal
        logger.debug("list data_source")

        if id is not None:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            if isinstance(id,list):
                logger.debug("List of the following instances: "+str(id))
                for element in id:
                    logger.debug("List of "+str(element))
                    endpoint = "v1/data_source/file/" + element
                    response = self.connection.send_request("GET", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))

                    endpoint = "v1/data_source/mqtt/" + element
                    response = self.connection.send_request("GET", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))

        else:
            logger.error("No ids to list")
            sys.exit(0)

    def delete(self, id):
        logger.debug("Delete data_source "+str(id))
        if id is not None:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            if isinstance(id,list):
                try:
                    logger.debug("List of the following instances: "+str(id))
                    for element in id:
                        logger.debug("List of "+str(element))
                        self.element_to_erase =element

                        endpoint = "v1/data_source/file/" + element
                        response = self.connection.send_request("DELETE", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))
                        self.erase_id(self.id_path,element)

                        endpoint = "v1/data_source/mqtt/" + element
                        response = self.connection.send_request("DELETE", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))
                        self.erase_id(self.id_path, element)

                except Exception as e:
                    self.erase_id(self.element_to_erase)
                    logger.error(e)

        else:
            logger.error("No ids to delete")
            sys.exit(0)


    def add(self, filepath, id=None):
        logger.debug("Add data_source")
        #project_dir = os.path.dirname(os.path.abspath(__file__))

        #if os.path.isabs(filepath):
            #data_file = filepath
        #else:
            #data_file = os.path.join(project_dir, filepath)

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

        if id is not None:
            logger.debug("id found for data_source add")
            logger.debug("id "+id)
            if "mqtt" in payload:
                logger.debug("mqtt with id")
                endpoint = "v1/data_source/mqtt/"+str(id)
                self.connection.send_request("PUT", endpoint, payload, headers)
            else:
                logger.debug("file with id")
                endpoint = "v1/data_source/file/"+str(id)
                self.connection.send_request("PUT", endpoint, payload, headers)

        else:
            if "mqtt" in payload:
                logger.debug("mqtt")
                endpoint = "v1/data_source/mqtt"

            else:
                logger.debug("file")
                endpoint = "v1/data_source/file"

            try:
                response = self.connection.send_request("POST", endpoint, payload, headers)
                if response["Data-Source-Id"] is not None:
                    logger.debug("Id: " + str(response["Data-Source-Id"]))
                    self.store("id.config",response["Data-Source-Id"])
            except Exception as e:
                logger.error(e)
                sys.exit(0)

    def store(self, path, data):
        if os.path.isfile(path):
            data_to_store = "\n" + data
            with open(path, 'a+') as outfile:
                outfile.write(data_to_store)
        else:
            with open(path, 'w') as outfile:
                outfile.write(data)

        logger.info("input data saved into memory")

    def get_id(self, path, number=None):

        if os.path.isfile(path):
            logger.debug("Path exists")
            with open(path, "r") as myfile:
                id = myfile.read().splitlines()
        else:
            id=None
        logger.debug("Ids present in this session: " + str(id))
        if id is not None:
            logger.debug("Working id " + str(id[-1]))
        logger.debug("number  "+str(number))
        if number is not None:
            if "all" in number:
                return id
            else:
                logger.error("Please write all or give the id")
                sys.exit(0)
        else:
            if id is not None:
                return [id[-1]]
            else:
                return None


    def erase_id(self, path, id):
        if os.path.isfile(path):
            try:
                id_from_file = self.get_id(path,"all")
                values=[]
                for element in id_from_file:
                    if id in element:
                        continue
                    else:
                        values.append(element)
                if len(values)==0:
                    os.remove(path)
                    logger.debug("File "+path+" erased")
                else:
                    with open(path, 'w') as outfile:
                        for item in values:
                            outfile.write("%s\n" % item)
            except Exception as e:
                logger.error(e)