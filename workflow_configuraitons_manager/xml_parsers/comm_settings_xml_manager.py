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

# Co-Simulator's import
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import enums
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import xml_tags
# from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import constants
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers.xml_manager import XmlManager


class CommunicationSettingsXmlManager(XmlManager):
    """
        XML Manager for the Communication Settings XML file
    """
    # __ric__to_be_deleted__ __co_simulation_parameters_for_json_dict = []

    def initialize_xml_elements(self):
        # TO BE DONE: there should be a global XML file where tags are defined
        self._component_xml_tag = xml_tags.CO_SIM_XML_CO_SIM_COMM_SETTINGS_ROOT_TAG

    def _build_variables_dict_from_xml_main_dicts(self):
        """
            Avoiding the presence of the <variable></variables> section on the XML file

        :return:

            XML_OK: Mimicking <variables> section parsing process was successful.
        """

        return enums.XmlManagerReturnCodes.XML_OK

    def _build_parameters_dict_from_xml_main_dicts(self):
        """
            Avoiding the presence of the <parameters> ... </parameters> section on the XML file

        :return:

            XML_OK: Mimicking <parameters> ... </parameters> section parsing process was successful.
        """

        return enums.XmlManagerReturnCodes.XML_OK

    def build_particular_sections_dicts(self):
        """
            - Implements the abstract method which is called at the end of the
            Co-Simulation XML file dissection process.
            - Converts into INTEGER those members of the dictionary whose value is expected to be numerical.

        :return:
            XML_VALUE_ERROR -> When some string cannot be converted into INTEGER
            XML_OK:         -> All the values were converted into INTEGER as expected.
        """

        #
        # processing the communication dictionary with the following format:
        # {
        #   'ORCHESTRATOR': {'MIN': '59100', 'MAX': '59120', 'MAX_TRIES': '20'},
        #   'COMMAND_CONTROL': {'MIN': '59121', 'MAX': '59150', 'MAX_TRIES': '30'},
        #   'APPLICATION_COMPANION': {'MIN': '59150', 'MAX': '59200', 'MAX_TRIES': '50'}
        # }
        # 2022-09-21: So far all the components will be treated similarly,
        #             meaning MAX MIN MAX_TRIES being INTEGER
        #
        for key, value in self._main_xml_sections_dicts_dict.items():
            # key -> represents a CO-SIM Component, e.g. ORCHESTRATOR

            try:
                value['MIN'] = int(value['MIN'])
                value['MAX'] = int(value['MAX'])
                value['MAX_TRIES'] = int(value['MAX_TRIES'])
            except ValueError:
                self._logger.error(ValueError)
                return enums.XmlManagerReturnCodes.XML_VALUE_ERROR

        return enums.XmlManagerReturnCodes.XML_OK

    def get_communication_settings_dict(self):
        """
            Returns the dictionary representing the Communication Setting XML file sections

            :return:
                A dictionary representing the content of the Communication Setting XML config file
        """

        # getting the dictionary from the parent class
        return self._main_xml_sections_dicts_dict
