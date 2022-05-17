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


# Co-Sim's imports


def node_text_to_datatype(node=None):
    l_node_datatype = node.attrib.get('datatype')
    if l_node_datatype:
        l_node_datatype = l_node_datatype.upper()

        if 'INTEGER' == l_node_datatype or 'INT' == l_node_datatype:
            return int(node.text)
        elif 'FLOAT' == l_node_datatype:
            return float(node.text)
        elif 'STRING' == l_node_datatype:
            return node.text  # assigned as it is on the XML file
        else:
            return None


class Xml2ClassParser:
    """
        XML Parser to create a class based on the passed XML PATH+FILENAME
    """

    def __init__(self, input_xml_path_filename=None, logger=None):
        self.__params_dict = None
        self.__input_xml_path_filename = input_xml_path_filename
        self.__logger = logger
        self.__parse_xml_and_create_dict()
        self.__create_attributes_from_dict()

    def __create_attributes_from_dict(self):
        for key in self.__params_dict:
            setattr(self, key, self.__params_dict[key])

    def __parse_xml_and_create_dict(self):
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
                    self.__logger.debug(f'start,MODEL found: model={is_model}')
                    processing_model = True
                    # model_element_id = id(node)
                    model_dict = {'model': is_model}  # NOTE: is_model contains the name of the model per se
                    continue

                has_datatype = node.attrib.get('datatype')
                if has_datatype:
                    if 'DICTIONARY' == has_datatype.upper():
                        processing_dictionary = True
                        dictionary_dict = {}
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
                    if 'DICTIONARY' == has_datatype.upper():
                        if processing_model:
                            model_dict[node.tag] = dictionary_dict
                            continue
                        self.__params_dict[node.tag] = dictionary_dict
                        continue

                # individual element
                if processing_element:
                    processing_element = False
                    if processing_dictionary:
                        dictionary_dict[node.tag] = node_text_to_datatype(node=node)
                        continue

                    if processing_model:
                        model_dict[node.tag] = node_text_to_datatype(node=node)
                        continue

                    self.__params_dict[node.tag] = node_text_to_datatype(node=node)

    # def __parse_xml_and_create_attributes(self):
    #     """
    #         Parses XML file and creates the object attributes upon XML elements.
    #     :return:
    # 
    #         CO_SIM_OK
    #     """
    #     self.__params_dict = {}
    # 
    #     with open(self.__input_xml_path_filename) as parameters_file:
    #         tree = ET.parse(parameters_file)
    # 
    #         # getting elements defined under <parameters><parameters>...</parameters></parameters> section
    #         parameters_root = tree.find('.//parameters')
    # 
    #         for node in parameters_root.iter():
    #             parameter_datatype = node.attrib.get('datatype')
    #             if parameter_datatype:
    #                 parameter_datatype = parameter_datatype.upper()
    #             parameter_name = node.tag
    #             parameter_value = node.text
    # 
    #             if 'INTEGER' == parameter_datatype:
    #                 self.__params_dict[parameter_name] = int(parameter_value)
    #             elif 'FLOAT' == parameter_datatype:
    #                 self.__params_dict[parameter_name] = float(parameter_value)
    #             elif 'STRING' == parameter_datatype:
    #                 self.__params_dict[parameter_name] = parameter_value  # assigned as it is on the XML file
    #             else:
    #                 self.__params_dict[parameter_name] = None  # since there is no datatype defined
    # 
    #     return enums.XmlManagerReturnCodes.XML_OK

    def get_parameters_dict(self):
        return self.__params_dict
