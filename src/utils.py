"""
Created on Jan 25 17:53 2019

@author: nishit
"""

import os
import logging, os, sys
import ntpath
import re
import json


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Utils:


    def store(self, path, data):
        #logger.debug("Storing data")
        #logger.debug("type data "+str(type(data)))
        folder_path=os.path.dirname(os.path.abspath(path))
        #logger.debug("folder path "+str(folder_path))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


        if os.path.isfile(path):
            if isinstance(data, str):
                data_to_store = "\n" + data
                with open(path, 'a+') as outfile:
                    outfile.write(data_to_store)
            elif isinstance(data, dict):
                logger.debug("entered to the dict")
                ids=self.get_id(path,"all")
                logger.debug("ids " + str(ids))
                logger.debug("ids[0] " + str(ids[0]))
                ids_to_store=[]
                for element in ids:
                    logger.debug("element "+str(element))
                    ids_to_store.append(element)
                ids_to_store.append(data)
                logger.debug("ids "+str(ids_to_store))
                with open(path, 'w') as outfile:
                    outfile.write(json.dumps(ids_to_store, indent=4, sort_keys=True))
        else:
            if isinstance(data,str):
                with open(path, 'w') as outfile:
                    outfile.write(data)
            elif isinstance(data, dict):
                with open(path, 'w') as outfile:
                    ids=[data]
                    outfile.write(json.dumps(ids, indent=4, sort_keys=True))


        logger.debug("input data saved in "+str(path))

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
                logger.debug("id_1 "+str(id))
                logger.debug("id[-1] " + str(id[-1]))
                return [json.loads(id[-1])]
            else:
                return None

    def erase_id(self, path, id, host):
        path_new = host + "-" + path
        if os.path.isfile(path_new):
            try:
                id_from_file = self.get_id(path,"all", self.command_to_execute["host"])
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



    def erase_id_erase(self, path, id):
        if os.path.isfile(path):
            try:
                id_from_file = self.get_id(path,"all", self.command_to_execute["host"])
                values=[]
                for element in id_from_file:
                    if id in element:
                        continue
                    else:
                        values.append(element)
                if len(values)==0:
                    os.remove(path)
                    logger.debug("File "+path+" erased")
                else:
                    with open(path, 'w') as outfile:
                        for item in values:
                            outfile.write("%s\n" % item)
            except Exception as e:
                logger.error(e)

