"""
Created on Jan 25 17:53 2019

@author: nishit
"""

import json
import logging
import ntpath
import os
import re
import sys

import pandas as pd
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
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def isFile(self, path):
        if os.path.isfile(path):
            return True
        else:
            return False

    def deleteFile(self, path):
        os.remove(path)

    def getFolderPath(self, path):
        return os.path.dirname(os.path.abspath(path))

    def store(self, path, data_list_of_dicts):
        #logger.debug("Storing data")
        #logger.debug("type data "+str(type(data)))
        folder_path = self.getFolderPath(path)
        #logger.debug("folder path "+str(folder_path))
        self.createFolderPath(folder_path)

        if os.path.isfile(path):
            if isinstance(data_list_of_dicts, list):
                logger.debug("entered to the dict")
                ids = self.get_id(path, "all")
                logger.debug("ids " + str(ids))
                ids_to_store = []

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
                    ids = data_list_of_dicts
                    outfile.write(json.dumps(ids, indent=4, sort_keys=True))

        logger.debug("input data saved in "+str(path))

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
            id = None

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
        path_new = path
        logger.debug("id erase "+str(id))
        if os.path.isfile(path_new):
            try:
                id_from_file = self.get_id(path, "all")
                values = []
                for element in id_from_file:
                    #logger.debug("element "+str(element))
                    for key in element.keys():
                        element_to_compare = element[key]
                    if not id in element_to_compare:
                        values.append(element)
                #logger.debug("values "+str(values))
                os.remove(path_new)
                if len(values) == 0:
                    logger.debug("File "+path_new+" erased")
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
                                col_header_name = col_header[cell_col_num+1]

                                if "MQTT" in col_header_name or col_header_name == "":
                                    sheet.write(cell_row_num + first_row, cell_col_num + 1,
                                                cell_value, cell_format)
                                else:
                                    sheet.merge_range(first_row, cell_col_num + 1,
                                                      last_row, cell_col_num + 1,
                                                      "", cell_format)
