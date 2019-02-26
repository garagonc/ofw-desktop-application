"""
Created on Jan 25 17:53 2019

@author: nishit
"""

import os
import logging
import os
import sys
import shutil
import ntpath
import re
import json
import pandas as pd
import copy
import xlsxwriter as xl


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class Utils:

    def __init__(self):
        self.sheets = ['inputs', 'outputs', 'start']
        self.col_headers = {'inputs': ['Input_name',
                                       'value',
                                       'or filename',
                                       '',
                                       'or MQTT params',
                                       'Description'],
                            'outputs': ['Output_name',
                                        '',
                                        'MQTT params',
                                        'Description'],
                            'start': ['configs',
                                      'Value',
                                      'Description']}
        self.default_cell_values = {'inputs': [['', '', 'url', '', ''],
                                               ['', '', 'topic', '', ''],
                                               ['', '', 'qos', '', '']],
                                    'outputs': [['url', '', ''],
                                                ['topic', '', ''],
                                                ['qos', '', '']],
                                    'start': [['', '']]
                                    }

    def createFolderPath(self, folder_path):
        folder_path = self.get_path(folder_path)
        #logger.debug("folder path "+str(folder_path))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


    def isFile(self, path):
        path = self.get_path(path)
        if os.path.isfile(path):
            return True
        else:
            return False

    def deleteFile(self, path):
        path = self.get_path(path)
        if self.isFile(path):
            try:
                os.remove(path)
            except Exception as e:
                logger.error(e)
        else:
            logger.error("Path not existing")

    def delete_folder(self, folder_path):
        folder_path = self.get_path(folder_path)
        shutil.rmtree(folder_path, ignore_errors=True)

    def delete_files_instances(self, id_list):
        for element in id_list:
            for model_name in element.keys():
                #logger.debug("element "+str(element))
                instance_name = self.get_instance_name([element])
                model_name = model_name
                folder = "instances"
                instance_path = os.path.join(folder, model_name, instance_name) + ".xlsx"
                if self.isFile(instance_path):
                    try:
                        os.remove(instance_path)
                    except Exception as e:
                        logger.error(e)
                else:
                    logger.error("Path not existing")

    def get_all_files_from_folder(self, folder_path):
        folder_path = self.get_path(folder_path)
        #logger.debug("folder path get all files "+str(folder_path))
        if os.path.isdir(folder_path):
            if not self.is_dir_empty(folder_path):
                values = []
                for the_file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, the_file)
                    try:
                        if os.path.isfile(file_path):
                            file = re.sub("\.(.*)", "", the_file)
                            values.append(file)
                    except Exception as e:
                        logger.error(e)
                return values
            else:
                return None
        else:
            return None

    def get_all_folder_names(self, folder_path):
        folder_path = self.get_path(folder_path)
        if os.path.isdir(folder_path):
            if not self.is_dir_empty(folder_path):
                values = []
                for the_file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, the_file)
                    try:
                        if os.path.isdir(file_path):
                            values.append(the_file)
                    except Exception as e:
                        logger.error(e)

                return values
            else:
                return None
        else:
            return None

    def delete_all_files_from_folder(self, folder_path):
        folder_path = self.get_path(folder_path)
        for the_file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def is_dir_empty(self, folder_path):
        folder_path = self.get_path(folder_path)
        for dirpath, dirnames, files in os.walk(folder_path):
            if files or dirnames:
                return False
            if not files or dirnames:
                return True

    def getFolderPath(self, path):
        return os.path.dirname(os.path.abspath(path))


    def get_path(self, relative_path):
        path_to_send= os.path.abspath(relative_path)
        #logger.debug("abs path "+str(path_to_send))
        return path_to_send

    def store(self, path, data_list_of_dicts):
        path = self.get_path(path)
        logger.debug("path "+str(path))
        self.createFolderPath(path)

        if isinstance(data_list_of_dicts, list):
            logger.debug("Storing the data")
            #path_to_write=self.get_path(path)
            with open(path, 'w') as outfile:
                ids = data_list_of_dicts
                outfile.write(json.dumps(ids, indent=4, sort_keys=True))
            logger.debug("input data saved in " + str(path))
        else:
            logger.debug("Storing the data 2 " + str(type(data_list_of_dicts)) )
            #path_to_write = self.get_path(path)
            with open(path, 'w') as outfile:
                outfile.write(data_list_of_dicts)
            logger.debug("input data saved in " + str(path))

    def store_as_excel(self, path, data, id):
        try:
            folder_path = self.getFolderPath(path)
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
            msg = "stored in "+str(path)
            return msg
        except Exception as e:
            logger.error(e)

    def get_host(self, path):
        #logger.debug("getting ids")
        path = self.get_path(path)
        if os.path.isfile(path):
            with open(path, "r") as myfile:
                host = myfile.read()
        else:
            host = None
        return host

    def instance_exist(self, model_name, instance_name):
        folder = "instances"
        path = os.path.join(folder, model_name, instance_name) + ".xlsx"
        path = self.get_path(path)
        if os.path.isfile(path):
            return True
        else:
            return False

    def model_folder_exist(self, model_name):
        folder = "instances"
        path = os.path.join(folder, model_name)
        path = self.get_path(path)
        if os.path.isdir(path):
            return True
        else:
            return False

    def get_id(self, path, number=None, model_name_input=None, instance_name_input=None):
        """Erase one id from the id.config file

            Arguments:
                path {str} -- Path of the id.config
                number {str} -- possibilities "all" or None
                model_name_input {str} -- model_name to erase. Posible "all"
                instance_name_input {str} -- instance_name to erase. Possible "all"
        """

        #logger.debug("getting id")
        path = self.get_path(path)
        if os.path.isfile(path):
            with open(path, "r") as myfile:
                id = json.load(myfile)
                if id is None:
                    return None
                #logger.debug("id "+str(id))
        else:
            return None

        if number is not None:
            if "all" in number:
                return id
            else:
                logger.error("Please write all or give the id")
                sys.exit(0)

        elif model_name_input is not None:
            if "all" in model_name_input:
                dict_1 = {}
                for list_1 in id:
                    # logger.debug("List of " + str(list_1))
                    for model_name in list_1.keys():
                        if not "None" in model_name:
                            # logger.debug("model_name " + str(model_name))
                            dict_1[model_name] = list_1[model_name]
                #logger.debug("dict_1 " + str(dict_1))
                #logger.debug("len dict_1 " + str(len(dict_1)))
                if len(dict_1) > 0:
                    return [dict_1]
                else:
                    return None
            else:
                # returns last id used with the given model_name
                if instance_name_input is None:
                    #logger.debug("Instance name not present")
                    dict_1 = {}
                    for element in id:
                        #logger.debug("element "+str(element))
                        if model_name_input in element.keys():

                            dict_1 = element
                    if len(dict_1) == 0:

                        return None

                    list_1 = []
                    for key in dict_1.keys():

                        if len(dict_1[key]) > 1:

                            list_1.append(dict_1[key][-1])
                            dict_1[key] = list_1
                    #logger.debug("dict_1 "+str(dict_1))
                    return [dict_1]

                else:
                    #logger.debug("Instance name and model_name present")
                    #logger.debug("id "+str(id))

                    # return all the ids for the given model name
                    if "all" in instance_name_input:
                        logger.debug("All instance names are being collected")

                        dict_1 = {}
                        for list_1 in id:
                            # logger.debug("List of " + str(list_1))
                            for model_name in list_1.keys():
                                if model_name_input == model_name:
                                    # logger.debug("model_name " + str(model_name))
                                    dict_1[model_name] = list_1[model_name]
                        #logger.debug("dict_1 " + str(dict_1))
                        #logger.debug("len dict_1 " + str(len(dict_1)))
                        if len(dict_1) > 0:
                            return [dict_1]
                        else:
                            return None

                    # returns the id(s) with the given model and instance names
                    else:
                        dict_1 = {}
                        for list_1 in id:
                            #logger.debug("List of " + str(list_1))
                            for model_name in list_1.keys():
                                if model_name_input in model_name:
                                    #logger.debug("model_name " + str(model_name))
                                    list_id = []
                                    for element in list_1[model_name]:
                                        #logger.debug("eleemtn "+str(element))

                                        for instance_name in element.keys():
                                            if instance_name_input == instance_name:
                                                list_id.append(element)
                                                #logger.debug("list_id " + str(list_id))
                                    if len(list_id) > 0:
                                        dict_1[model_name] = list_id
                                    else:
                                        return None

                        #logger.debug("dict_1 " + str(dict_1))
                        #logger.debug("len dict_1 " + str(len(dict_1)))
                        if len(dict_1) > 0:
                            return [dict_1]
                        else:
                            return None

        else:
            dict_1 = id[-1]
            list_1 = []
            for key in dict_1.keys():
                if len(dict_1[key]) > 1:
                    list_1.append(dict_1[key][-1])
                    dict_1[key] = list_1
            #logger.debug("dict_1 " + str(id[-1]))
            return [dict_1]

    def get_id_list(self, data):
        data_to_return = []
        if data is not None:
            for list_1 in data:
                #logger.debug("List of " + str(list_1))
                for model_name in list_1.keys():
                    #logger.debug("model_name " + str(model_name))
                    for list_2 in list_1[model_name]:
                        for instance_name in list_2.keys():
                            element_id = list_2[instance_name]
                            #logger.debug("id " + str(element_id) + " instance_name " + str(instance_name))
                            data_to_return.append(element_id)
            return data_to_return
        else:
            return None

    def is_model_name(self, data_to_compare,  model_name_input):
        #logger.debug("data_to_compare "+str(data_to_compare)+" type "+str(type(data_to_compare)))
        #logger.debug("model name input " + str(model_name_input)+" type "+str(type(model_name_input)))
        for element in data_to_compare:
            #logger.debug("element "+str(element))
            for model_name in element.keys():
                #logger.debug("model name "+str(model_name))
                if model_name_input == model_name:
                    #logger.debug("model name found in ids")
                    return True
        return False

    def get_instance_name(self, id_list):

        for element in id_list:
            for model_name in element.keys():
                for element_2 in element[model_name]:
                    for instance_name in element_2:
                        if instance_name:
                            return instance_name
                    else:
                        return None

    def integrate_id_in_model_name(self, path, id, model_name_input, instance_name_input):
        path = self.get_path(path)
        if os.path.isfile(path):
            try:
                id_from_file = self.get_id(path, "all")

                if id is not None:
                    # logger.debug("Entered to id list"+str(id_list))

                    if model_name_input is not None:

                        if self.is_model_name(id_from_file, model_name_input):

                            for list_1 in id_from_file:
                                for model_name in list_1.keys():

                                    if model_name_input in model_name:
                                        values_list_2 = []
                                        for list_2 in list_1[model_name]:

                                            for instance_name in list_2.keys():
                                                values_list_2.append(list_2)
                                        dict_add = {str(instance_name_input): id}
                                        values_list_2.append(dict_add)
                                        #logger.debug("values_list_2 "+str(values_list_2))
                                        list_1[model_name] = values_list_2
                                        #logger.debug("list_1 " + str(list_1))
                            #logger.debug("id_from_file " + str(id_from_file))

                            return id_from_file
                        else:

                            for list_1 in id_from_file:
                                list_1[model_name_input] = [{str(instance_name_input): id}]
                            return id_from_file
                    else:

                        dict_1 = {}
                        dict_1[str(model_name_input)] = [{str(instance_name_input): id}]
                        id_from_file.append(dict_1)
                        return id_from_file
            except Exception as e:
                logger.error(e)
                sys.exit(0)
        else:
            dict_1 = {}
            dict_1[str(model_name_input)] = [{str(instance_name_input): id}]
            return [dict_1]

    def convert_string_to_id(self, data_string, model_name=None, instance_name=None):
        value = {}
        value[model_name] = [{str(instance_name): data_string}]
        return [value]
    # enters one id as a list

    def relocate_id(self, id_list, id_from_file, model_name_input=None, instance_name_input=None):
        try:
            if id_list is not None:
                    #logger.debug("Entered to id list"+str(id_list))

                values = []
                instance_dict_temp = {}
                for list_1 in id_from_file:
                    for model_name in list_1.keys():
                        instance_dict = {}

                        values_list_2 = []
                        temp_value = None
                        for list_2 in list_1[model_name]:
                            for instance_name in list_2.keys():
                                element_to_compare = list_2[instance_name]
                                for ids in id_list:
                                    if not ids in element_to_compare:
                                        values_list_2.append(list_2)
                                    else:
                                        temp_value = list_2
                                    #logger.debug("values_list_2 " + str(values_list_2))
                        if temp_value is not None:
                            values_list_2.append(temp_value)
                            instance_dict_temp[model_name] = values_list_2
                        else:
                            instance_dict[model_name] = values_list_2
                        #logger.debug("values_list_2_2 " + str(values_list_2))
                        #logger.debug("instance dict "+str(instance_dict))
                        if len(instance_dict) > 0:
                            values.append(instance_dict)
                values.append(instance_dict_temp)
                return values
                #logger.debug("values " + str(values))
        except Exception as e:
            logger.error(e)

    # enters one id

    def erase_id(self, path, id, model_name_input=None):
        """Erase one id from the id.config file

                Arguments:
                    path {str} -- Path of the id.config
                    id {str} -- Id to be erased from the config
                    model_name_input {str} -- model_name to erase
                """
        path = self.get_path(path)
        #logger.debug("id to erase "+str(id))
        if os.path.isfile(path):
            try:
                id_from_file = self.get_id(path, "all")
                #logger.debug("id from file "+str(id_from_file))
                if id is not None:
                    #logger.debug("Entered to id")
                    values = []
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
                            if len(values_list_2) > 0:
                                instance_dict[model_name] = values_list_2
                            #logger.debug("instance dict "+str(instance_dict))
                            if len(instance_dict) > 0:
                                values.append(instance_dict)
                            #logger.debug("values " + str(values))

                elif model_name_input is not None:
                    #logger.debug("Entered to model_name")
                    values = []
                    for list_1 in id_from_file:
                        for model_name in list_1.keys():
                            instance_dict = {}
                            #logger.debug("model_name "+str(model_name)+ " model_name_input "+str(model_name_input) )
                            if not model_name_input in model_name:
                                instance_dict[model_name] = list_1[model_name]
                            #logger.debug("instance dict "+str(instance_dict)+" len "+str(len(instance_dict)))
                            if len(instance_dict) > 0:
                                values.append(instance_dict)
                            #logger.debug("values " + str(values))

                #logger.debug("values model_name" + str(values))

                if len(values) == 0:
                    os.remove(path_new)
                    logger.debug("File " + path_new + " erased")
                else:
                    self.store(path, values)
            except Exception as e:
                logger.error(e)

    def generate_xlsx_instance_config(self, data, filepath):
        """Generate excel sheet for instance configuration

        Arguments:
            data {dict} -- Input data with list of config to be filled
            filepath {str} -- File path of the excel file to be created
        """
        filepath = self.get_path(filepath)
        if os.path.isfile(filepath):
            logger.error("File already exists. Cannot overwrite file")
        else:

            with xl.Workbook(filepath) as workbook:

                row_header_format = workbook.add_format({'align': 'center',
                                                         'bold': True,
                                                         'valign': 'vcenter'})
                col_header_format = workbook.add_format({'align': 'center',
                                                         'bold': True,
                                                         'valign': 'vcenter'})
                cell_format = workbook.add_format()

                # Formatting information
                border_size = 2
                col_header_width = 30
                normal_col_width = 20
                short_col_width = 5

                row_header_format.set_border(border_size)
                col_header_format.set_border(border_size)
                cell_format.set_border(border_size)

                # Generate worksheets and format
                for worksheet_name in self.sheets:
                    sheet = workbook.add_worksheet(worksheet_name)

                    # Create column headers
                    col_header = self.col_headers[worksheet_name]
                    for col_num, col_value in enumerate(col_header):
                        sheet.write(0, col_num,
                                    col_value, col_header_format)

                        # Column formatting
                        sheet.set_column(col_num, col_num, normal_col_width)

                        # Widen first column
                        if col_num == 0:
                            sheet.set_column(col_num, col_num, col_header_width)
                        # Shorten empty column
                        if col_value == "":
                            sheet.set_column(col_num, col_num, short_col_width)

                    # Create row headers and format rows based on default inputs
                    row_header = data[worksheet_name]
                    cell_values = self.default_cell_values[worksheet_name]
                    for row_num, row_value in enumerate(row_header):

                        # Different formatting for start config sheet
                        if worksheet_name == "start":
                            sheet.write(row_num + 1, 0,
                                        row_value, cell_format)

                            for cell_row_num, cell_row in enumerate(cell_values):
                                for cell_col_num, cell_value in enumerate(cell_row):
                                    sheet.write(cell_row_num + row_num + 1,
                                                cell_col_num + 1,
                                                cell_value, cell_format)
                            # skip the rest of the code for start config
                            continue

                        # Merge every three cells for row header
                        first_row = 1 + (row_num * 3)
                        last_row = first_row + 2
                        sheet.merge_range(first_row, 0,
                                          last_row, 0,
                                          row_value, row_header_format)

                        for cell_row_num, cell_row in enumerate(cell_values):
                            for cell_col_num, cell_value in enumerate(cell_row):
                                # Get col name and set formatting per row or per merged range
                                col_header_name = col_header[cell_col_num + 1]

                                if "MQTT" in col_header_name or col_header_name == "":
                                    sheet.write(cell_row_num + first_row, cell_col_num + 1,
                                                cell_value, cell_format)
                                else:
                                    sheet.merge_range(first_row, cell_col_num + 1,
                                                      last_row, cell_col_num + 1,
                                                      "", cell_format)

    def read_data_from_xlsx_instance_config(self, filepath):
        """Reads data from excel config file, parses it, and returns it as dict

        Arguments:
            filepath {str} -- Filepath to the excel config file

        Returns:
            dict -- Python dict of inputs, outputs, and start config
        """
        filepath = self.get_path(filepath)
        if not os.path.isfile(filepath):
            logger.error(f"Error: Excel file at {filepath} is missing")
            return

        # Read file
        excel_data = pd.read_excel(filepath, sheet_name=None)

        # Extract inputs sheet
        inputs = excel_data["inputs"]
        inputs.drop(labels=["Description", inputs.columns[3]], axis=1, inplace=True)
        inputs.fillna("empty_input_values", inplace=True)

        generic_input_mqtt = {}
        generic_input_dataset = {}
        input_fields = []

        # Extract data from input sheet and store as dict
        for row_num in range(0, len(inputs), 3):
            input_value_name = inputs.loc[row_num]["Input_name"]
            input_fields.append(input_value_name)

            input_values = inputs.loc[row_num][1:]

            for key, value in input_values.items():
                if value == "empty_input_values":
                    continue

                if "MQTT params" in key:
                    host = inputs.loc[row_num]["or MQTT params"]
                    topic = inputs.loc[row_num + 1]["or MQTT params"]
                    qos = inputs.loc[row_num + 2]["or MQTT params"]

                    if input_value_name in generic_input_mqtt:
                        logger.error(
                            f"ERROR: Duplicate values: \
                                Please fill only one column for {input_value_name} in inputs sheet")
                        return

                    if (host != "empty_input_values"
                            and topic != "empty_input_values"
                            and qos != "empty_input_values"):
                        generic_input_mqtt[input_value_name] = {
                            "mqtt": {
                                "qos": qos,
                                "host": host,
                                "topic": topic
                            }
                        }
                    else:
                        logger.error(f"ERROR: \
                                    MQTT params for {input_value_name} in inputs sheet is missing.")
                        return

                    continue

                if "filename" in key:
                    #path=os.path.join("instances",value)
                    folder_path=self.getFolderPath(filepath)
                    path = os.path.join(folder_path, value)
                    logger.debug("path xlsx "+str(path))
                    if os.path.isfile(path):
                        data_from_file = pd.read_excel(path, header=None)

                        if input_value_name in generic_input_dataset:
                            logger.error(f"ERROR: Duplicate values: \
                                        Please fill only one column for {input_value_name}")
                            return

                        processed_data_from_file = data_from_file[data_from_file.columns[0]]
                        generic_input_dataset[input_value_name] = processed_data_from_file.tolist()
                    else:
                        logger.error(
                            f"ERROR: Filename {value} provided for input {input_value_name} \
                                in inputs sheet is missing. Please check again")
                        return
                    continue

                if input_value_name in generic_input_mqtt:
                    logger.error(
                        f"ERROR: Duplicate values: \
                            Please fill only one column for {input_value_name} in inputs sheet")
                    return

                generic_input_mqtt[input_value_name] = value

        filled_inputs = set(generic_input_mqtt).union(set(generic_input_dataset))
        missing_inputs = set(input_fields).difference(filled_inputs)

        for input_name in missing_inputs:
            logger.error(f"ERROR: {input_name} field in inputs sheet is missing")
            return

        # Extract outputs sheet
        outputs = excel_data["outputs"].drop(labels=["Description"], axis=1)
        outputs.drop(outputs.columns[1], axis=1, inplace=True)
        outputs.fillna("empty_input_values", inplace=True)

        generic_output_data = {}
        output_fields = []

        # Extract data from output sheet and store as dict
        for row_num in range(0, len(outputs), 3):
            output_value_name = outputs.loc[row_num]["Output_name"]
            output_fields.append(output_value_name)

            host = outputs.loc[row_num]["MQTT params"]
            topic = outputs.loc[row_num + 1]["MQTT params"]
            qos = outputs.loc[row_num + 2]["MQTT params"]

            if (host != "empty_input_values"
                    and topic != "empty_input_values"
                    and qos != "empty_input_values"):
                generic_output_data[output_value_name] = {
                    "mqtt": {
                        "qos": qos,
                        "host": host,
                        "topic": topic
                    }
                }
            else:
                logger.error(f"ERROR: MQTT params for {output_value_name} in inputs sheet is missing.")
                return

        missing_outputs = set(output_fields).difference(set(generic_output_data))
        for output_name in missing_outputs:
            logger.error(f"ERROR: {output_name} field in outputs sheet is missing")
            return

        # Extract data from start sheet and store it as dict
        start_config = excel_data["start"].drop(labels=["Description"], axis=1)
        start_config.fillna("empty_input_values", inplace=True)

        generic_start_config_data = {}
        for i, row in start_config.iterrows():
            config_name = row["configs"]
            config_value = row["Value"]
            if config_value != "empty_input_values":
                generic_start_config_data[config_name] = config_value
            else:
                logger.error(f"ERROR: {config_name} field in start config sheet is missing")
                return

        # Store all data in a dict
        data_from_xlsx = {
            "inputs": {
                "dataset": {
                    "generic": generic_input_dataset
                },
                "mqtt": {
                    "generic": generic_input_mqtt
                }
            },
            "outputs": {
                "generic": generic_output_data
            },
            "start": generic_start_config_data
        }

        return data_from_xlsx
