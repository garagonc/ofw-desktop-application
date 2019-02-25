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
                                id_list = self.util.get_id_list(id)
                                self.start(str(value[0]), id_list)
                            else:
                                self.start(str(value[0]), None)
                        else:
                            #id = self.util.convert_string_to_id(str(value[1]))
                            id_list=[value[1]]
                            self.start(str(value[0]), id_list)
                    elif len(value) == 1:
                        id = self.util.get_id(self.id_path, None)

                        if id is not None:
                            id_list = self.util.get_id_list(id)
                            self.start(str(value[0]), id_list)
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
                    if len(value) == 2:
                        instance_name=value[1]
                        model_name = value[0]
                        id = self.util.get_id(self.id_path, "all")
                        if self.util.is_model_name(id, model_name):
                            if instance_name == "all":
                                id = self.util.get_id(self.id_path, None, model_name, "all")
                                id_list = self.util.get_id_list(id)
                            elif self.util.instance_exist(model_name,instance_name):
                                id = self.util.get_id(self.id_path,None,model_name, instance_name)
                                id_list = self.util.get_id_list(id)
                                #logger.debug("id_list "+str(id_list))
                            else:
                                logger.error("Instance name is missing or wrong")
                                sys.exit(0)
                        else:
                            logger.error("Model name is missing or wrong")
                            sys.exit(0)

                    elif len(value) == 1:
                        model_name=value[0]
                        id = self.util.get_id(self.id_path, "all")
                        if "all" in model_name:
                            id_list = self.util.get_id_list(id)
                        elif self.util.is_model_name(id,model_name):
                            id = self.util.get_id(self.id_path, None, model_name, None)
                            id_list = self.util.get_id_list(id)
                        else:
                            id_list = [value[0]]
                    elif len(value) == 0:
                        id = self.util.get_id(self.id_path, None)
                        id_list = self.util.get_id_list(id)
                    else:
                        logger.error("Too many arguments for command stop")
                        sys.exit(0)

                    if id_list is not None:
                        self.stop(id_list)
                    else:
                        self.stop(None)

                elif key is "status":
                    self.status()

                elif key is "restart":
                    #logger.debug("length: "+str(len(value)))
                    #logger.debug("value "+str(value))
                    if len(value) == 3:
                        model_name = value[0]
                        filepath = value[1]
                        id = value[2]
                        self.restart(model_name, filepath, id)
                    elif len(value) == 2:
                        model_name = value[0]
                        filepath = value[1]
                        self.restart(model_name,filepath)
                    elif len(value) == 1:
                        model_name = value[0]
                        self.restart(model_name)
                    else:
                        self.restart(None)


    def restart(self, model_name, filepath=None, id=None):

        logger.debug("restart")
        self.restart_flag=True
        folder="instances"
        #instance_path = os.path.join(folder,model_name,filepath)

        #self.util.isFile()
        data_to_compare = self.util.get_id(self.id_path, "all")
        if self.util.is_model_name(data_to_compare, model_name):
            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            if filepath is None:
                id = self.util.get_id(self.id_path, None, model_name, None)
                id_list = self.util.get_id_list(id)
                logger.debug("id_list " + str(id_list))
                logger.debug("Stopping the requested instances ")
                self.stop(id_list)
                logger.debug("Starting the requested instances ")
                instance_name_list = self.util.get_instance_name(id)
                self.start_instance(model_name, instance_name_list)
                sys.exit(0)

            else:
                if  filepath == "all":
                    id = self.util.get_id(self.id_path, None, model_name, "all")
                    id_list = self.util.get_id_list(id)
                    logger.debug("id_list " + str(id_list))
                    logger.debug("Stopping the requested instances ")
                    self.stop(id_list)
                    logger.debug("Starting the requested instances ")
                    #instance_name_list = self.util.get_instance_name(id_list)
                    self.start_instance(model_name,"all")
                    sys.exit(0)
                elif self.util.instance_exist(model_name, filepath):
                    if id is None:
                        instance_name = filepath
                        id = self.util.get_id(self.id_path,None,model_name,instance_name)
                        id_list = self.util.get_id_list(id)
                        logger.debug("id_list "+str(id_list))
                        logger.debug("Stopping the requested instances ")
                        self.stop(id_list)
                        logger.debug("Starting the requested instances ")
                        instance_name_list = self.util.get_instance_name(id)
                        self.start_instance(model_name, instance_name_list)
                        sys.exit(0)
                    else:
                        logger.error("If you entered an instance name, you don't need to enter an id")
                        sys.exit(0)
                elif self.util.isFile(filepath):
                    #filepath introduced
                    try:
                        with open(filepath, "r") as myfile:
                            payload = myfile.read()
                            payload = json.loads(payload)
                    except Exception as e:
                        logger.error(e)
                        sys.exit(0)

                    if id is None:
                        id = self.util.get_id(self.id_path, None, model_name, None)
                        id_list = self.util.get_id_list(id)
                        logger.debug("id_list " + str(id_list))
                        logger.debug("Stopping the requested instances ")
                        self.stop(id_list)

                    elif id == "all":
                        id = self.util.get_id(self.id_path, None, model_name, "all")
                        id_list = self.util.get_id_list(id)
                        logger.debug("id_list " + str(id_list))
                        logger.debug("Stopping the requested instances ")
                        self.stop(id_list)

                    else:
                        id_list = id
                        logger.debug("id_list " + str(id_list))
                        logger.debug("Stopping the requested instances ")
                        self.stop(id_list)

                    logger.debug("Starting the requested instances ")
                    """instance_status = {}
                    #logger.debug("id list " + str(id_list))
                    status = self.status()
                    for element_id in id_list:
                        if status:
                            for key1, body in status["status"].items():
                                for key, value in body.items():
                                    if "config" in key:
                                        instance_status = value
                                        break

                        if payload is None:
                            payload = instance_status
                        else:
                            payload = json.loads(payload)"""

                    self.start(payload, id_list)
                else:
                    logger.error("Enter please  a correct filepath or instance_name. \"all\" will start all instances from the model name already started before")
                    sys.exit(0)
        elif model_name == "all":
            id = self.util.get_id(self.id_path, None, "all", None)
            logger.debug("model names "+str(id))
            id_list = self.util.get_id_list(id)
            logger.debug("id_list " + str(id_list))
            logger.debug("Stopping the requested instances ")
            self.stop(id_list)
            logger.debug("Starting the requested instances ")
            for element in id:
                for model_name_element in element.keys():
                    self.start_instance(model_name_element, "all")
            sys.exit(0)
        elif model_name is None:
            logger.error("Enter please a model name or \"all\"")
            sys.exit(0)
        else:
            logger.error("Model name not existing or has not been started yet. Use first --start")
            sys.exit(0)




        """if id is not None:
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
            sys.exit(0)"""

    def start_instance(self, model_name, instance_name):
        logger.debug("start instance")

        if self.util.model_folder_exist(model_name):

            if instance_name is not None:
                folder = "instances"
                if instance_name == "all":
                    folder_path = os.path.join(folder, model_name)
                    instance_names = self.util.get_all_files_from_folder(folder_path)
                    logger.debug("Instance names "+str(instance_names))
                else:
                    if self.util.instance_exist(model_name,instance_name):
                        instance_names = [instance_name]
                    logger.debug("Instance names " + str(instance_names))

                for element in instance_names:

                    #Read data from file
                    instance_path = os.path.join(folder, model_name, element) + ".xlsx"
                    try:
                        data = self.util.read_data_from_xlsx_instance_config(instance_path)
                        logger.debug("data " + str(data))
                    except Exception as e:
                        logger.debug(e)
                    self.input_data = self.data["input"]
                    self.output_data = self.data["output"]
                    self.start_data = self.data["start"]


                    id = self.util.get_id(self.id_path, None, model_name, element)
                    logger.debug("instance_name " + str(element))
                    logger.debug("id " + str(id))
                    if id is None:
                        # if the id is not present, we make a POST of the input
                        logger.debug("Registering inputs")
                        if isinstance(self.input_data, dict):
                            if len(self.input_data) > 0:
                                logger.debug("Adding inputs")
                                self.input_object.add(self.input_data, None, model_name, element, self.id_path,
                                                      self.connection)
                                id = self.util.get_id(self.id_path, None, model_name, element)
                                id_list = self.util.get_id_list(id)
                            else:
                                logger.error("No input configuration present")
                                sys.exit(0)
                        else:
                            logger.error("Input configuration is not a dictionary")
                            sys.exit(0)
                    else:
                        id_list = self.util.get_id_list(id)
                        id_from_file = self.util.get_id(self.id_path, "all")
                        data_relocated = self.util.relocate_id(id_list, id_from_file)
                        logger.debug("Data relocated")
                        self.util.store(self.id_path, data_relocated)
                        logger.debug("Ids relocated in memory")

                        logger.debug("Registering inputs")
                        if isinstance(self.input_data, dict):
                            if len(self.input_data) > 0:
                                logger.debug("Adding inputs with id")
                                self.input_object.add(self.input_data, id_list, model_name, element, self.id_path,
                                                      self.connection)
                            else:
                                logger.error("No input configuration present")
                                sys.exit(0)
                        else:
                            logger.error("Input configuration is not a dictionary")
                            sys.exit(0)


                    logger.debug("Registering outputs")

                    # after adding the input the otuput is always added
                    if isinstance(self.output_data, dict):
                        if len(self.output_data) > 0:
                            #id = self.util.get_id(self.id_path, None, model_name, instance_name)
                            self.output_object.add(self.output_data, id_list, self.connection)
                    else:
                        logger.error("Output configuration is not a dictionary")
                        sys.exit(0)

                    logger.debug("Starting the system")
                    # After input and output we start ofw
                    if isinstance(self.start_data, dict):
                        if len(self.start_data) > 0:
                            # start the platform
                            #id = self.util.get_id(self.id_path, None, model_name, instance_name)
                            self.start(self.start_data, id_list)
                        else:
                            logger.error("No start configuration present")
                            sys.exit(0)
                    else:
                        logger.error("Input configuration is not a dictionary")
                        sys.exit(0)
            else:
                logger.error("Cite please the instance with instance_name or the word \"all\". If there is not an instance with that name, add please the instance with --instance_add")
                sys.exit(0)
        else:
            logger.error("Add please the instance with --instance_add")
            sys.exit(0)


            #call get instance values with model_name and instance_name and stores it in data


            #call a function to check if the model_name and instance_name are already associate to an id





    def start(self, filepath, id):

        logger.debug("start")
        id_list=id
        #id_list = self.util.get_id_list(id)



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
                #logger.debug("#################################################################")
                #logger.debug("Id list to start: "+str(id_list))
                #logger.debug("#################################################################")
                #id_list = self.util.get_id_list(id)
                #logger.debug("id list " + str(id_list))
                for element_id in id_list:
                    #logger.debug("id "+str(element))
                    endpoint = "v1/optimization/start/" + str(element_id)
                    response = self.connection.send_request("PUT", endpoint, payload, headers)
                    logger.debug("#################################################################")
                    logger.debug("Id to start: " + str(element_id))
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))
                    logger.debug("#################################################################")
        else:
            logger.error("Id is missing as parameter")
            sys.exit(0)




    def stop(self, id, model_name=None, instance_name=None):
        logger.debug("stop")

        if id is not None:
            payload = ""

            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }

            if isinstance(id,list):
                #logger.debug("Stoping the following instances: "+str(id))
                #logger.debug("#################################################################")
                #logger.debug("Id list to stop " + str(id))
                #logger.debug("#################################################################")
                for element_id in id:
                    endpoint = "v1/optimization/stop/" + element_id
                    response = self.connection.send_request("PUT", endpoint, payload, headers)
                    logger.debug("#################################################################")
                    logger.debug("Id to stop " + str(element_id))
                    logger.debug(json.dumps(response, indent=4, sort_keys=True))
                    logger.debug("#################################################################")

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

