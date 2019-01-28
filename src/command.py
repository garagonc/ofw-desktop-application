"""
Created on Jan 25 17:53 2019

@author: garagon
"""

import os

class Command:


    def execute(self, connection, command_to_execute):
        self.connection=connection
        self.command_to_execute=command_to_execute

        print("command_to_execute" + str(command_to_execute))
        if command_to_execute["command"] == "-start":
            self.start()
        elif command_to_execute["command"] == "-stop":
            self.stop()
        elif command_to_execute["command"] == "-status":
            self.status()


    def start(self):
        #need to use host
        # curl may not work on windows terminal
        print("list data_source")

        payload = ""
        filepath = self.command_to_execute["filepath"]
        # data_file = os.path.join(project_dir, filepath)
        print("path: " + filepath)
        payload = ""
        with open(filepath, "r") as myfile:
            payload = myfile.read()

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }
        if "id" in self.command_to_execute:
            id = self.command_to_execute["id"]
            endpoint = "v1/command/start/" + id
            self.connection.send_request("PUT", endpoint, payload, headers)
        else:
            print("Id is missing as parameter")


    def stop(self):
        print("Delete data_source "+str(self.command_to_execute["id"]))
        if "id" in self.command_to_execute:
            id = self.command_to_execute["id"]
            endpoint = "v1/command/stop/" + id
            self.connection.send_request("PUT", endpoint, payload, headers)
        else:
            print("Id is missing as parameter")



    def status(self):
        print("Add data_source")
        payload=""

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        endpoint = "v1/command/status"
        self.connection.send_request("GET", endpoint, payload, headers)


