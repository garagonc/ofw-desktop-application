"""
Created on Jan 25 17:53 2019

@author: garagon
"""
import logging, os
import sys
import json
from src.utils import Utils

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class Command:

    folder_path="config"
    path = "id.config"
    restart_flag=False

    def __init__(self):
        self.util = Utils()

    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        path = self.command_to_execute["host"] + "-" + self.path
        self.id_path = os.path.join(self.folder_path, path)

        for key, value in command_to_execute["command"].items():
            if value is not None:
                if key is "start":
                    #logger.debug("length: "+str(len(value)))
                    if len(value) == 2:
                        if "all" in value:
                            id = self.util.get_id(self.id_path,"all")
                            if id is not None:
                                self.start(str(value[0]), id)
                            else:
                                self.start(str(value[0]), None)
                        else:
                            self.start(str(value[0]), str(value[1]))
                    elif len(value) == 1:
                        id = self.util.get_id(self.id_path, None)

                        if id is not None:
                            self.start(str(value[0]), id)
                        else:
                            self.start(str(value[0]), None)
                    else:
                        logger.error("Configuration file is missing")
                        sys.exit(0)

                elif key is "stop":
                    #logger.debug("length " + str(len(value)))

                    if len(value) == 1:
                        if "all" in value:
                            id = self.util.get_id(self.id_path,"all")
                        else:
                            logger.debug("Value " + str(value))
                            id = value
                    else:
                        id = self.util.get_id(self.id_path, None)
                    if id is not None:
                        self.stop(id)
                    else:
                        self.stop(None)
                elif key is "status":
                    self.status()

                elif key is "restart":
                    #logger.debug("length: "+str(len(value)))
                    #logger.debug("value "+str(value))
                    if len(value) == 3:
                        if "all" in value:
                            id = self.util.get_id(self.id_path,"all")
                            if id is not None:
                                self.restart(str(value[0]), str(value[1]),id)
                            else:
                                logger.error("No ids to restart. Id is missing")
                                sys.exit(0)
                        else:
                            self.restart(str(value[0]), str(value[1]),[str(value[2])])
                    elif len(value) == 2:
                        id = self.util.get_id(self.id_path, None)
                        if id is not None:
                            self.restart(str(value[0]),str(value[1]), id)
                        else:
                            self.restart(str(value[0]), str(value[1]), None)
                    elif len(value) == 1:
                        id = self.util.get_id(self.id_path, None)
                        if id is not None:
                            self.restart(str(value[0]),None, id)
                        else:
                            self.restart(str(value[0]),None, None)
                    else:
                        id = self.util.get_id(self.id_path, None)
                        if id is not None:
                            self.restart(None, None, id)
                        else:
                            self.restart(None, None, None)


    def restart(self, model_name, filepath=None, id=None):

        logger.debug("restart")
        self.restart_flag=True

        if filepath == "None":
            #logger.debug("fileptah is str none")
            payload = None
        elif filepath is None:
            #logger.debug("fileptah is none")
            payload = None
        else:
            #logger.debug("fileptah is str 2")
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

        if id is not None:
            self.stop(id)

            logger.debug("Restarting the following instances: " + str(id))
            instance_status = {}
            id_list = self.util.get_id_list(id)
            logger.debug("id list " + str(id_list))
            for element_id in id_list:
                status = self.status()

                if status:
                    for key1, body in status["status"].items():
                        for key, value in body.items():
                            if "config" in key:
                                instance_status = value
                                break

                if payload is None:
                    payload=instance_status
                else:
                    payload=json.loads(payload)

                if model_name == "None":
                    pass
                elif model_name is None:
                    pass
                else:
                    payload["model_name"] = model_name


                payload = json.dumps(payload)
                endpoint = "v1/optimization/start/" + str(element_id)
                response = self.connection.send_request("PUT", endpoint, payload, headers)
                logger.debug(json.dumps(response, indent=4, sort_keys=True))
        else:
            logger.error("Id is missing as parameter")
            sys.exit(0)


    def start(self, filepath, id):

        logger.debug("start")

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
            #logger.debug("id "+str(id)+" type "+str(type(id)))
            if isinstance(id,list):
                logger.debug("Starting the following instances: "+str(id))
                id_list = self.util.get_id_list(id)
                logger.debug("id list " + str(id_list))
                for element_id in id_list:
                    #logger.debug("id "+str(element))
                    endpoint = "v1/optimization/start/" + str(element_id)
                    response = self.connection.send_request("PUT", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))

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
                id_list = self.util.get_id_list(id)
                logger.debug("id list " + str(id_list))
                for element_id in id_list:
                    endpoint = "v1/optimization/stop/" + element_id
                    response = self.connection.send_request("PUT", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))

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

        endpoint = "v1/optimization/status"
        response = self.connection.send_request("GET", endpoint, payload, headers)
        if not self.restart_flag:
            logger.debug(json.dumps(response, indent=4, sort_keys=True))
        return response

