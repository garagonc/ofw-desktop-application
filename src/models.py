"""
Created on Jan 25 17:53 2019

@author: nishit
"""
import subprocess as sub

class Models:

    @staticmethod
    def execute(command_to_execute, host_info):
        if command_to_execute["command"] == "list":
            Models.list(host_info)

    @staticmethod
    def list(host_info):
        #need to use host
        # curl may not work on windows terminal
        p = sub.Popen(["curl", "-X GET http://192.168.99.100:8080/v1/models -H 'Cache-Control: no-cache"], stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = p.communicate()
        print(output)


