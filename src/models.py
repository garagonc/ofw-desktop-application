"""
Created on Jan 25 17:53 2019

@author: nishit
"""

import os

class Models:


    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        print("command_to_execute" + str(command_to_execute))
        if command_to_execute["command"] == "-list":
            self.list()
        elif command_to_execute["command"] == "-delete":
            self.delete()
        elif command_to_execute["command"] == "-add":
            self.add()


    def list(self):
        #need to use host
        # curl may not work on windows terminal
        print("list")
        payload = ""
        headers = {
            'cache-control': "no-cache"
        }
        self.connection.send_request("GET","v1/models",payload, headers)


    def delete(self):
        print("Delete "+str(self.command_to_execute["model_name"]))
        model_name=self.command_to_execute["model_name"]
        if "all" in model_name:
            payload = ""
            headers = {
                'cache-control': "no-cache"
            }
            self.connection.send_request("DELETE", "v1/models", payload, headers)
        else:
            payload = ""
            headers = {
                'cache-control': "no-cache"
            }
            endpoint= "v1/models/" + model_name
            self.connection.send_request("DELETE", endpoint, payload, headers)
        #if self.command_to_execute[""]


    def add(self):
        print("Add")
        model_name = self.command_to_execute["model_name"]
        print("model_name. "+model_name)
        #project_dir=os.path.dirname(os.path.abspath(__file__))
        #project_dir="/usr/src/app"
        #print("dir "+str(project_dir))
        filepath=self.command_to_execute["filepath"]
        #data_file = os.path.join(project_dir, filepath)
        print("path: "+filepath)
        payload=""
        with open(filepath,"r") as myfile:
            payload=myfile.read()

        headers = {
            'cache-control': "no-cache"
        }
        endpoint = "v1/models/upload/" + model_name
        self.connection.send_request("POST", endpoint, payload, headers)

