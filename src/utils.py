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

    def store(self, path, data_list_of_dicts):
        #logger.debug("Storing data")
        #logger.debug("type data "+str(type(data)))
        folder_path=self.getFolderPath(path)
        #logger.debug("folder path "+str(folder_path))
        self.createFolderPath(folder_path)

        if os.path.isfile(path):
            if isinstance(data_list_of_dicts, list):
                logger.debug("entered to the dict")
                ids=self.get_id(path,"all")
                logger.debug("ids " + str(ids))
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

    def get_id(self, path, number=None):
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
        else:
            if id is not None:
                #logger.debug("id_1 "+str(id))
                #logger.debug("id[-1] " + str(id[-1])+" type "+str(type(id[-1])))
                return [id[-1]]
            else:
                return None

    def erase_id(self, path, id):
        path_new =  path
        logger.debug("id erase "+str(id))
        if os.path.isfile(path_new):
            try:
                id_from_file = self.get_id(path,"all")
                values=[]
                for element in id_from_file:
                    #logger.debug("element "+str(element))
                    for key in element.keys():
                        element_to_compare=element[key]
                    if not id in element_to_compare:
                        values.append(element)
                #logger.debug("values "+str(values))
                os.remove(path_new)
                if len(values)==0:
                    logger.debug("File "+path_new+" erased")
                else:
                    self.store(path,values)
            except Exception as e:
                logger.error(e)
