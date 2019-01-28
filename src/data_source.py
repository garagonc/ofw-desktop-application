"""
Created on Jan 25 17:53 2019

@author: garagon
"""

import os

class Data_source:


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
        print("list data_source")

        payload = ""
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }
        if "id" in self.command_to_execute:
            id = self.command_to_execute["id"]
            endpoint = "v1/data_source/file/" + id
            self.connection.send_request("GET",endpoint,payload, headers)
        else:
            endpoint = "v1/data_source"
            self.connection.send_request("GET", endpoint, payload, headers)


    def delete(self):
        print("Delete data_source "+str(self.command_to_execute["id"]))
        id=self.command_to_execute["id"]
        if "all" in id:
            payload = ""
            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }
            endpoint = "v1/data_source/"+id
            self.connection.send_request("DELETE", endpoint, payload, headers)
        else:
            payload = ""
            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }
            endpoint= "v1/data_source/file/" + id
            self.connection.send_request("DELETE", endpoint, payload, headers)
            endpoint = "v1/data_source/mqtt/" + id
            self.connection.send_request("DELETE", endpoint, payload, headers)



    def add(self):
        print("Add data_source")
        #project_dir=os.path.dirname(os.path.abspath(__file__))
        #project_dir="/usr/src/app"
        #print("dir "+str(project_dir))
        filepath=self.command_to_execute["filepath"]
        #data_file = os.path.join(project_dir, filepath)
        print("path: "+filepath)
        payload=""
        with open(filepath,"r") as myfile:
            payload=myfile.read()
        print("payload type "+str(type(payload)))
        print(payload)
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        if "id" in self.command_to_execute:
            id = self.command_to_execute["id"]
            endpoint = "v1/data_source/mqtt/"+id
            self.connection.send_request("PUT", endpoint, payload, headers)
        else:
            if "mqtt" in payload:
                print("mqtt")
                endpoint = "v1/data_source/mqtt"
                self.connection.send_request("POST", endpoint, payload, headers)
            else:
                print("file")
                endpoint = "v1/data_source/file"
                self.connection.send_request("POST", endpoint, payload, headers)

