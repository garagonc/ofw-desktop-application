"""
Created on Jan 25 17:53 2019

@author: garagon
"""
import sys
import logging, os
import json


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
class Data_output:

    id_path="id.config"

    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        for key, value in command_to_execute["data_output"].items():
            if value is not None:
                if key is "list":
                    if len(value) == 1:
                        if "all" in value:
                            id = self.get_id(self.id_path,"all", self.command_to_execute["host"])
                        else:
                            id = value
                    else:
                        id = self.get_id(self.id_path, None, self.command_to_execute["host"])
                    if id is not None:
                        self.list(id)
                    else:
                        self.list(None)

                elif key is "delete":
                    if len(value) == 1:
                        if "all" in value:
                            id = self.get_id(self.id_path,"all", self.command_to_execute["host"])
                        else:
                            id = value
                    else:
                        id = self.get_id(self.id_path, None, self.command_to_execute["host"])
                    if id is not None:
                        self.delete(id)
                    else:
                        self.delete(None)
                elif key is "add":
                    if len(value) == 2:
                        self.add(str(value[0]), str(value[1]))
                    else:
                        id=self.get_id(self.id_path, None, self.command_to_execute["host"])
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
                for element in id:
                    logger.debug("List of "+str(element))
                    endpoint = "v1/outputs/" + element
                    response = self.connection.send_request("GET", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))
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
                for element in id:
                    #logger.debug("List of "+str(element))
                    endpoint = "v1/outputs/dataset/" + element
                    response = self.connection.send_request("DELETE", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))

                    endpoint = "v1/outputs/mqtt/" + element
                    response = self.connection.send_request("DELETE", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))
                    self.erase_id(self.id_path,element)

        else:
            logger.error("No ids to delete")
            sys.exit(0)


    def add(self, filepath, id=None):
        logger.debug("Add data_output")

        #logger.debug("path: "+filepath)
        payload=""
        with open(filepath,"r") as myfile:
            payload=myfile.read()

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        if id is not None:
            #logger.debug("id found for data_ouput")
            #logger.debug("id "+str(id))
            endpoint = "v1/outputs/mqtt/"+id[0]
            response=self.connection.send_request("PUT", endpoint, payload, headers)
            logger.debug(json.dumps(response, indent=4, sort_keys=True))
        else:
            logger.error("Id is missing as parameter")
            sys.exit(0)

    def get_id(self, path, number, host):
        path = host + "-" + path

        if os.path.isfile(path):
            #logger.debug("Path exists")
            with open(path, "r") as myfile:
                id = myfile.read().splitlines()
        else:
            id = None
        #logger.debug("Ids present in this session: " + str(id))
        if id is not None:
            pass
            #logger.debug("Working id " + str(id[-1]))
        #logger.debug("number  " + str(number))
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
                id_from_file = self.get_id(path,"all", self.command_to_execute["host"])
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