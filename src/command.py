"""
Created on Jan 25 17:53 2019

@author: garagon
"""
import logging, os
import sys
import json
from src.utils import Utils
from src.data_source import Data_source
from src.control import Data_output

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class Command:

    folder_path="config"
    path = "id.config"
    restart_flag=False

    def __init__(self):
        self.util = Utils()
        self.input_object=Data_source()
        self.output_object=Data_output()

        self.data = {}
        self.data["input"] = {
            "ESS": {
                "SoC_Value": {
                    "mqtt": {
                        "host": "mosquito_S4G",
                        "topic": "input/HOUSE_1/SoC_Value",
                        "qos": 1
                    }
                },
                "meta": {
                    "ESS_Max_SoC": 0.9,
                    "ESS_Max_Discharge_Power": 2500,
                    "ESS_Max_Charge_Power": 2500,
                    "ESS_Min_SoC": 0.2,
                    "ESS_Capacity": 3560
                }
            },
            "global_control": {
                "ESS_Control": {
                    "mqtt": {
                        "host": "mosquito_S4G",
                        "topic": "input/HOUSE_1/ESS_Control",
                        "qos": 1
                    }
                }
            },
            "photovoltaic": {
                "P_PV": {
                    "mqtt": {
                        "host": "mosquito_S4G",
                        "topic": "input/HOUSE_1/P_PV",
                        "qos": 1
                    }
                },
                "meta": {
                    "PV_Inv_Max_Power": 1300,
                    "City": "Fur",
                    "Country": "Denmark"
                }
            },
            "grid": {
                "meta": {
                    "Q_Grid_Max_Export_Power": 750,
                    "P_Grid_Max_Export_Power": 1550
                }
            }
        }
        self.data["output"] ={
            "ESS": {
                "P_ESS_Output": {
                    "mqtt": {
                        "host": "mosquito_S4G",
                        "topic": "output/House_1/P_ESS",
                        "qos": 1
                    }
                }
            },
            "grid": {
                "P_Grid_Output": {
                    "mqtt": {
                        "host": "mosquito_S4G",
                        "topic": "output/House_1/P_Grid",
                        "qos": 1
                    }
                }
            },
            "photovoltaic": {
                "P_PV_Output": {
                    "mqtt": {
                        "host": "mosquito_S4G",
                        "topic": "output/House_1/P_PV",
                        "qos": 1
                    }
                }
            }
        }
        self.data["start"]={
            "control_frequency": 30,
            "horizon_in_steps": 24,
            "dT_in_seconds": 3600,
            "model_name": "testModel2",
            "repetition": -1,
            "solver": "ipopt"
        }

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
                            id = self.util.convert_string_to_id(str(value[1]))
                            self.start(str(value[0]), id)
                    elif len(value) == 1:
                        id = self.util.get_id(self.id_path, None)

                        if id is not None:
                            self.start(str(value[0]), id)
                        else:
                            self.start(str(value[0]), None)
                    else:
                        logger.error("Configuration file is missing")
                        sys.exit(0)
                elif key is "start_instance":
                    # logger.debug("length: "+str(len(value)))
                    if len(value) == 2:
                        self.start_instance(str(value[0]), str(value[1]))
                    elif len(value) == 1:
                        self.start_instance(str(value[0]),None)
                    else:
                        logger.debug("Introduce please the model_name")
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

    def start_instance(self, model_name, instance_name):
        logger.debug("start instance")
        all_ids=self.util.get_id(self.id_path, "all")
        if self.util.instance_exist(model_name,instance_name):
        #if self.util.is_model_name(all_ids,model_name):
            #if self.util.instance_exist(model_name,instance_name):
            #call get instance values with model_name and instance_name and stores it in data
            folder = "instances"
            instance_path = os.path.join(folder, model_name, instance_name) + ".xlsx"
            data=self.util.read_data_from_xlsx_instance_config(instance_path)
            logger.debug("data "+str(data))
            self.input_data = self.data["input"]
            self.output_data =  self.data["output"]
            self.start_data = self.data["start"]

            #call a function to check if the model_name and instance_name are already associate to an id
            id_list=self.util.get_id(self.id_path, None, model_name, instance_name)
            if instance_name is None:
                instance_name=self.util.get_instance_name(id_list)
            logger.debug("instance name "+str(instance_name))
            logger.debug("id_list " + str(id_list))
            #logger.debug(" len " + str(len(id_list)))

            if id_list is not None:
                id = self.util.get_id_list(id_list)
                id_from_file = self.util.get_id(self.id_path, "all")
                data_relocated=self.util.relocate_id(id,id_from_file)
                self.util.store(self.id_path,data_relocated)
                logger.debug("Ids relocated in memory")

            else:
                #if the id is not present, we make a POST of the input
                if isinstance(self.input_data,dict):
                    if len(self.input_data) > 0:
                        logger.debug("Adding inputs")
                        self.input_object.add(self.input_data,None,model_name,instance_name, self.id_path, self.connection)
                    else:
                        logger.error("No input configuration present")
                        sys.exit(0)
                else:
                    logger.error("Input configuration is not a dictionary")
                    sys.exit(0)

            #after adding the input the otuput is always added
            if isinstance(self.output_data,dict):
                if len(self.output_data) > 0:
                    id=self.util.get_id(self.id_path,None,model_name,instance_name)
                    self.output_object.add(self.output_data,id,self.connection)
            else:
                logger.error("Output configuration is not a dictionary")
                sys.exit(0)

            #After input and output we start ofw
            if isinstance(self.start_data,dict):
                if len(self.start_data) > 0:
                    #start the platform
                    id = self.util.get_id(self.id_path, None, model_name, instance_name)
                    self.start(self.start_data,id)
                else:
                    logger.error("No start configuration present")
                    sys.exit(0)
            else:
                logger.error("Input configuration is not a dictionary")
                sys.exit(0)
        else:
            logger.error("Add please the instance with --instance_add")
            sys.exit(0)

    def start(self, filepath, id):

        logger.debug("start")

        id_list = self.util.get_id_list(id)



        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        if id is not None:
            if not isinstance(filepath, dict):
                try:
                    with open(filepath, "r") as myfile:
                        payload = myfile.read()

                    id_from_file = self.util.get_id(self.id_path, "all")
                    data_relocated = self.util.relocate_id(id_list, id_from_file)
                    self.util.store(self.id_path, data_relocated)
                    logger.debug("Ids relocated in memory")

                except Exception as e:
                    logger.error(e)
                    sys.exit(0)
            else:
                payload = json.dumps(filepath)
            #logger.debug("id "+str(id)+" type "+str(type(id)))
            if isinstance(id,list):
                logger.debug("Starting the following instances: "+str(id))
                #id_list = self.util.get_id_list(id)
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

