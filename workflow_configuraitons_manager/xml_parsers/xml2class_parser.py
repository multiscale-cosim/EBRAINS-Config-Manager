# ------------------------------------------------------------------------------
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor
#  license agreements; and to You under the Apache License, Version 2.0. "
#
# Forschungszentrum Jülich
#  Institute: Institute for Advanced Simulation (IAS)
#    Section: Jülich Supercomputing Centre (JSC)
#   Division: High Performance Computing in Neuroscience
# Laboratory: Simulation Laboratory Neuroscience
#       Team: Multi-scale Simulation and Design
#
# ------------------------------------------------------------------------------

from xml.etree.ElementTree import iterparse
import numpy as np


# Co-Sim's imports

class ConvertXmlNodeTextToDatatype(object):
    """
        XML's Node Data Conversion
    """

    #
    # TO BE DONE: A proper procedure of creation, since the XML file must be
    #             well-formed and so far, it is not being checked before
    #             going to parse it out.
    #
    def __init__(self):
        self.__integer_labels_list = ['INT', 'INTEGER']
        self.__string_labels_list = ['STR', 'STRING']

    def node_text_to_datatype(self, node=None):
        """
            Converts the node's text (data) into the specified datatype on the XML's node tag

        :param node:
            XML's node containing data to be transformed
        :return:
            The data converted as Python's data type
        """
        l_node_datatype = node.attrib.get('datatype')
        if l_node_datatype:
            l_node_datatype = l_node_datatype.upper()

            if l_node_datatype in self.__integer_labels_list:
                return int(node.text)
            elif 'FLOAT' == l_node_datatype:
                return float(node.text)
            elif l_node_datatype in self.__string_labels_list:
                return node.text  # assigned as it is on the XML file
            else:
                return None


class Xml2ClassParser:
    """
        XML Parser to create a class based on the passed XML PATH+FILENAME
    """

    #
    # TO BE DONE: Support for Python's list, tuples among others.
    #

    def __init__(self, input_xml_path_filename=None, logger=None):
        self.__dictionary_labels_list = ['DICT', 'DICTIONARY']
        self.__array_labels_list = ['ARR', 'ARRAY']  # numpy.array
        self.__convert_xml_node_text_to_datatype = ConvertXmlNodeTextToDatatype()
        self.__params_dict = None
        self.__input_xml_path_filename = input_xml_path_filename
        self.__logger = logger
        self.__parse_xml_and_create_dict()
        self.__create_attributes_from_dict()

    def __create_attributes_from_dict(self):
        """
            Creates the class (object) attributes from the dictionary,
            such attributes dictionary is filled up by the parser
            of the XML parameters parser
        :return:
        """
        for key in self.__params_dict:
            setattr(self, key, self.__params_dict[key])

    def __parse_xml_and_create_dict(self):
        """
            Fills up the attributes' dictionary by parsing the parameters XML file
        :return:
        """
        self.__params_dict = {}
        model_dict = {}
        dictionary_dict = {}

        processing_model = False
        processing_dictionary = False
        processing_element = False
        for (event, node) in iterparse(
                source=self.__input_xml_path_filename,
                events=['start', 'end'],
        ):

            if event == 'start':

                is_model = node.attrib.get('model')
                if is_model:
                    processing_model = True
                    # model_element_id = id(node)
                    model_dict = {'model': is_model}  # NOTE: is_model contains the name of the model per se
                    continue

                has_datatype = node.attrib.get('datatype')
                if not has_datatype:
                    pass
                else:
                    if has_datatype.upper() in self.__dictionary_labels_list:
                        processing_dictionary = True
                        dictionary_dict = {}
                    elif has_datatype.upper() in self.__array_labels_list:
                        processing_array = True
                        #  numpy_array = np.empty([1])
                    processing_element = True
                    continue

            if event == 'end':
                is_model = node.attrib.get('model')
                if is_model:
                    # all elements will be added as a dictionary
                    self.__params_dict[node.tag] = model_dict
                    processing_model = False
                    continue

                has_datatype = node.attrib.get('datatype')
                if has_datatype:
                    if has_datatype.upper() in self.__dictionary_labels_list:
                        processing_dictionary = False
                        if processing_model:
                            model_dict[node.tag] = dictionary_dict
                            continue
                        self.__params_dict[node.tag] = dictionary_dict
                        continue
                    elif has_datatype.upper() in self.__array_labels_list:
                        processing_array = False
                        array_sep = node.attrib.get('sep')
                        array_dtype = node.attrib.get('dtype')
                        if array_dtype:
                            tmp_np_array = np.fromstring(node.text, sep=array_sep, dtype=array_dtype)
                        else:
                            # default dtype float64
                            tmp_np_array = np.fromstring(node.text, sep=array_sep, dtype='float')

                        # assigning the numpy array to the proper "level"
                        if processing_model:
                            model_dict[node.tag] = tmp_np_array
                            continue
                        self.__params_dict[node.tag] = tmp_np_array
                        continue

                # individual element
                if processing_element:
                    processing_element = False
                    if processing_dictionary:
                        dictionary_dict[node.tag] = self.__convert_xml_node_text_to_datatype.node_text_to_datatype(
                            node=node)
                        continue

                    if processing_model:
                        model_dict[node.tag] = self.__convert_xml_node_text_to_datatype.node_text_to_datatype(node=node)
                        continue

                    self.__params_dict[node.tag] = self.__convert_xml_node_text_to_datatype.node_text_to_datatype(
                        node=node)

    def get_parameters_dict(self):
        return self.__params_dict
