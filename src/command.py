"""
Created on Jan 25 17:53 2019

@author: garagon
"""
import logging, os
import sys
import json


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class Command:

    id_path = "id.config"

    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        for key, value in command_to_execute["command"].items():
            if value is not None:
                if key is "start":
                    logger.debug("length: "+str(len(value)))
                    if len(value) == 2:
                        if "all" in value:
                            id = self.get_id(self.id_path,"all")
                            if id is not None:
                                self.start(str(value[0]), id)
                            else:
                                self.start(str(value[0]), None)
                        else:
                            self.start(str(value[0]), str(value[1]))
                    elif len(value) == 1:
                        id = self.get_id(self.id_path, None)

                        if id is not None:
                            self.start(str(value[0]), id)
                        else:
                            self.start(str(value[0]), None)
                    else:
                        logger.error("Configuration file is missing")
                        sys.exit(0)

                elif key is "stop":
                    logger.debug("length " + str(len(value)))

                    if len(value) == 1:
                        if "all" in value:
                            id = self.get_id(self.id_path,"all")
                        else:
                            logger.debug("Value " + str(value))
                            id = value
                    else:
                        id = self.get_id(self.id_path, None)
                    if id is not None:
                        self.stop(id)
                    else:
                        self.stop(None)
                elif key is "status":
                    self.status()


    def start(self, filepath, id):

        logger.debug("start")

        payload = ""

        logger.debug("path: " + filepath)
        payload = ""
        try:
            with open(filepath, "r") as myfile:
                payload = myfile.read()
        except Exception as e:
            logger.error(e)
            sys.exit(0)

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }
        #if self.command_to_execute["id"] is not None:
        if id is not None:
            logger.debug("id "+str(id)+" type "+str(type(id)))
            if isinstance(id,list):
                logger.debug("Starting the following instances: "+str(id))
                for element in id:
                    logger.debug("id "+str(element))
                    endpoint = "v1/command/start/" + str(element)
                    response = self.connection.send_request("PUT", endpoint, payload, headers)
                    logger.debug(response)
            else:
                logger.debug("Starting the following instances: "+str(id))
                endpoint = "v1/command/start/" + id
                response=self.connection.send_request("PUT", endpoint, payload, headers)
                logger.debug(response)
        else:
            logger.error("Id is missing as parameter")
            sys.exit(0)


    def stop(self, id):
        logger.debug("stop")

        if id is not None:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            if isinstance(id,list):
                logger.debug("Stoping the following instances: "+str(id))
                for element in id:
                    logger.debug("List of "+str(element))
                    endpoint = "v1/command/stop/" + element
                    response = self.connection.send_request("PUT", endpoint, payload, headers)
                    logger.debug(response)
            """else:
                logger.debug("Stoping the following instance: "+str(id))
                endpoint = "v1/command/stop/" + id
                response = self.connection.send_request("PUT", endpoint, payload, headers)
                logger.debug(response)
            """

        else:
            logger.error("Id is missing as parameter")
            sys.exit(0)



    def status(self):
        logger.debug("status")
        payload=""

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        endpoint = "v1/command/status"
        response = self.connection.send_request("GET", endpoint, payload, headers)
        logger.debug(json.dumps(response, indent=4, sort_keys=True))

    def get_id(self, path, number=None):

        if os.path.isfile(path):
            logger.debug("Path exists")
            with open(path, "r") as myfile:
                id = myfile.read().splitlines()
        else:
            id = None
        logger.debug("Ids present in this session: " + str(id))
        if id is not None:
            logger.debug("Working id " + str(id[-1]))
        logger.debug("number  " + str(number))
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

