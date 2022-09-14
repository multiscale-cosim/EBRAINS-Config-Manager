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

    def get_communication_settings_dict(self):
        """
            Returns the dictionary representing the Communication Setting XML file sections

            :return:
                A dictionary representing the content of the Communication Setting XML config file
        """

        # getting the dictionary from the parent class
        return self._main_xml_sections_dicts_dict
