"""
Created on Jan 25 17:53 2019

@author: nishit
"""

import os
import logging, os, sys
import ntpath
import re
import json
import pandas as pd
import copy


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Utils:

    def createFolderPath(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def isFile(self, path):
        if os.path.isfile(path):
            return True
        else:
            return False

    def deleteFile(self,path):
        os.remove(path)

    def getFolderPath(self,path):
        return os.path.dirname(os.path.abspath(path))

    def collect_store_ids_from_ofw(self,path):
        if not self.util.isFile(path):
            ids=self.list(None,"ids")

            ids_to_store = []
            for element in ids:
                ids_dict = {}
                ids_dict["None"]=  [{"None": element}]
                ids_to_store.append(ids_dict)
            self.util.store(path,ids_to_store)



    def store(self, path, data_list_of_dicts):
        folder_path=self.getFolderPath(path)
        self.createFolderPath(folder_path)

        if os.path.isfile(path):
            if isinstance(data_list_of_dicts, list):
                #logger.debug("entered to the dict")
                ids=self.get_id(path,"all")
                #logger.debug("ids " + str(ids))
                ids_to_store=[]

                for element in ids:
                    #logger.debug("element "+str(element))
                    ids_to_store.append(element)
                for element in data_list_of_dicts:
                    #logger.debug("element " + str(element))
                    ids_to_store.append(element)

                #logger.debug("ids "+str(ids_to_store))
                with open(path, 'w') as outfile:
                    outfile.write(json.dumps(ids_to_store, indent=4, sort_keys=True))
        else:
            if isinstance(data_list_of_dicts, list):
                with open(path, 'w') as outfile:
                    ids=data_list_of_dicts
                    outfile.write(json.dumps(ids, indent=4, sort_keys=True))


        logger.debug("input data saved in "+str(path))

    def store_as_excel(self, path, data, id):
        try:
            folder_path=self.getFolderPath(path)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # Create a Pandas dataframe from the data.
            df = data
            # Create a Pandas Excel writer using XlsxWriter as the engine.
            writer = pd.ExcelWriter(path, engine='xlsxwriter')
            # Convert the dataframe to an XlsxWriter Excel object.
            df.to_excel(writer, sheet_name='Sheet1')
            # Close the Pandas Excel writer and output the Excel file.
            writer.save()
            msg= "stored in "+str(path)
            return msg
        except Exception as e:
            logger.error(e)

    def get_host(self, path):
        if os.path.isfile(path):
            with open(path, "r") as myfile:
                host = myfile.read()
        else:
            host = None
        return host

    def get_id(self, path, number=None, model_name_input=None):
        #logger.debug("getting id")
        if os.path.isfile(path):
            with open(path, "r") as myfile:
                id = json.load(myfile)
                #logger.debug("id "+str(id))
        else:
            id=None

        if number is not None:
            if "all" in number:
                return id
            else:
                logger.error("Please write all or give the id")
                sys.exit(0)
        elif model_name_input is not None:
            if id is not None:
                dict_1={}
                for list_1 in id:
                    logger.debug("List of " + str(list_1))
                    for model_name in list_1.keys():
                        if model_name_input in model_name:
                            logger.debug("model_name " + str(model_name))
                            dict_1[model_name]=list_1[model_name]
                logger.debug("dict_1 " + str(dict_1))
                return [dict_1]
            else:
                return None
        else:
            if id is not None:
                dict_1=id[-1]
                list_1=[]
                for key in dict_1.keys():
                    if len(dict_1[key])>1:
                        list_1.append(dict_1[key][-1])
                        dict_1[key]=list_1
                logger.debug("dict_1 " + str(id[-1]))
                return [dict_1]
            else:
                return None

    def get_id_list(self, data):
        data_to_return=[]
        for list_1 in data:
            logger.debug("List of " + str(list_1))
            for model_name in list_1.keys():
                logger.debug("model_name " + str(model_name))
                for list_2 in list_1[model_name]:
                    for instance_name in list_2.keys():
                        element_id = list_2[instance_name]
                        logger.debug("id " + str(element_id) + " instance_name " + str(instance_name))
                        data_to_return.append(element_id)
        return data_to_return

    def erase_id(self, path, id, model_name_input=None):
        path_new =  path
        #logger.debug("id to erase "+str(id))
        if os.path.isfile(path_new):
            try:
                if id is not None:
                    logger.debug("Entered to id")
                    id_from_file = self.get_id(path,"all")
                    values=[]
                    for list_1 in id_from_file:
                        for model_name in list_1.keys():
                            instance_dict = {}
                            values_list_2 = []

                            for list_2 in list_1[model_name]:
                                for instance_name in list_2.keys():
                                    element_to_compare = list_2[instance_name]
                                    if not id in element_to_compare:
                                        values_list_2.append(list_2)
                                        #logger.debug("values_list_2 " + str(values_list_2))
                            instance_dict[model_name]=values_list_2
                            #logger.debug("instance dict "+str(instance_dict))
                            if len(instance_dict)>0:
                                values.append(instance_dict)
                            #logger.debug("values " + str(values)

                elif model_name_input is not None:
                    logger.debug("Entered to model_name")
                    id_from_file = self.get_id(path, "all")
                    values = []
                    for list_1 in id_from_file:
                        for model_name in list_1.keys():
                            instance_dict = {}
                            logger.debug("model_name "+str(model_name)+ " model_name_input "+str(model_name_input) )
                            if not model_name_input in model_name:
                                instance_dict[model_name] = list_1[model_name]
                            logger.debug("instance dict "+str(instance_dict)+" len "+str(len(instance_dict)))
                            if len(instance_dict)>0:
                                values.append(instance_dict)
                            logger.debug("values " + str(values))

                logger.debug("values model_name" + str(values))
                os.remove(path_new)
                if len(values) == 0:
                    logger.debug("File " + path_new + " erased")
                else:
                    self.store(path, values)
            except Exception as e:
                logger.error(e)
