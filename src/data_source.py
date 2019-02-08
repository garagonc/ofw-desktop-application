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
                    #logger.debug("length "+str(len(value)))
                    if len(value) == 1:
                        if "all" in value:
                            id = self.get_id(self.id_path,"all", self.command_to_execute["host"])
                        else:
                            logger.debug("Value "+str(value))
                            id = value
                    else:
                        id = self.get_id(self.id_path, None, self.command_to_execute["host"])
                    if id is not None:
                        logger.debug("id "+str(id))
                        self.delete(id)
                    else:
                        self.delete(None)
                elif key is "add":
                    if len(value) == 2:
                        logger.debug("Value 0 "+str(value[0]))
                        logger.debug("Value 1 " + str(value[1]))
                        self.add(str(value[0]), str(value[1]))
                    else:
                        logger.debug("Value 0 " + str(value[0]))
                        self.add(str(value[0]))


    def list(self, id):
        #need to use host
        # curl may not work on windows terminal
        logger.debug("list inputs")

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
                    endpoint = "v1/inputs/dataset/" + element
                    response = self.connection.send_request("GET", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))

                    endpoint = "v1/inputs/mqtt/" + element
                    response = self.connection.send_request("GET", endpoint, payload, headers)
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))

        else:
            logger.error("No ids to list")
            sys.exit(0)

    def delete(self, id):
        logger.debug("Delete input "+str(id))
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
                        #logger.debug("List of "+str(element))
                        self.element_to_erase =element

                        endpoint = "v1/inputs/dataset/" + element
                        response = self.connection.send_request("DELETE", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))
                        self.erase_id(self.id_path,element,self.command_to_execute["host"])

                        endpoint = "v1/inputs/mqtt/" + element
                        response = self.connection.send_request("DELETE", endpoint, payload, headers)
                        logger.debug(json.dumps(response, indent=4, sort_keys=True))
                        self.erase_id(self.id_path, element,self.command_to_execute["host"])

                except Exception as e:
                    self.erase_id(self.id_path,self.element_to_erase,self.command_to_execute["host"])
                    logger.error(e)

        else:
            logger.error("No ids to delete")
            sys.exit(0)


    def add(self, filepath, id=None):
        logger.debug("Add inputs")
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
                    self.store("id.config",response, self.command_to_execute["host"])
            except Exception as e:
                logger.error(e)
                sys.exit(0)

    def store(self, path, data, host):
        path=host+"-"+path
        if os.path.isfile(path):
            data_to_store = "\n" + data
            with open(path, 'a+') as outfile:
                outfile.write(data_to_store)
        else:
            with open(path, 'w') as outfile:
                outfile.write(data)

        logger.debug("input data saved into memory")

    def get_id(self, path, number, host):
        path = host + "-" + path
        #logger.debug("path "+path)
        if os.path.isfile(path):
            #logger.debug("Path exists")
            with open(path, "r") as myfile:
                id = myfile.read().splitlines()
        else:
            id=None
        #logger.debug("Ids present in this session: " + str(id))
        #if id is not None:
            #logger.debug("Working id " + str(id[-1]))

        #logger.debug("number  "+str(number))
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


    def erase_id(self, path, id, host):
        path_new = host + "-" + path
        #logger.debug("path "+str(path_new))
        if os.path.isfile(path_new):
            try:
                id_from_file = self.get_id(path,"all", self.command_to_execute["host"])
                #logger.debug("id_from_file "+str(id_from_file))
                values=[]
                for element in id_from_file:
                    #logger.debug("element "+str(element))
                    if not id in element:
                        values.append(element)
                logger.debug("values "+str(values))
                if len(values)==0:
                    os.remove(path_new)
                    logger.debug("File "+path_new+" erased")
                else:
                    with open(path_new, 'w') as outfile:
                        counter=0
                        for item in values:
                            if counter==0:
                                outfile.write("%s" % item)
                                counter=1
                            else:
                                outfile.write("\n%s" % item)
            except Exception as e:
                logger.error(e)