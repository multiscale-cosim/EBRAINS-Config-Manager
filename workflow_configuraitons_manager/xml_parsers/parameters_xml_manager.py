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
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import constants
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers.xml_manager import XmlManager


class ParametersXmlManager(XmlManager):
    """
        XML Manager for the Parameters XML file
    """
    __co_simulation_parameters_for_json_dict = []

    def initialize_xml_elements(self):
        # TO BE DONE: there should be a global XML file where tags are defined
        self._component_xml_tag = xml_tags.CO_SIM_XML_CO_SIM_PARAMS_ROOT_TAG

    def __build_parameters_for_json(self):
        """
            Build the the dictionary to be dumped into a file by means of json.dump

        :return:
            XML_TAG_ERROR - Tag not found in the Co-Simulation XML parameters files
            XML_OK - The dictionary to be dumped into a json files is ready
        """
        xml_co_sim_parameters_json_file = {}

        try:
            xml_co_sim_parameters_json_file = \
                self._main_xml_sections_dicts_dict[xml_tags.CO_SIM_XML_CO_SIM_PARAMS_JSON_FILE]
        except KeyError:
            self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                       xml_tags.CO_SIM_XML_CO_SIM_PARAMS_JSON_FILE,
                                                                       xml_tags.CO_SIM_XML_CO_SIM_PARAMS_JSON_FILE))
            return enums.XmlManagerReturnCodes.XML_TAG_ERROR

        # filename (remains the same)
        try:
            self.__co_simulation_parameters_for_json_dict[xml_tags.CO_SIM_XML_CO_SIM_PARAMS_FILENAME] = \
                xml_co_sim_parameters_json_file[xml_tags.CO_SIM_XML_CO_SIM_PARAMS_FILENAME]    
        except KeyError:
            self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                       xml_tags.CO_SIM_XML_CO_SIM_PARAMS_FILENAME,
                                                                       xml_tags.CO_SIM_XML_CO_SIM_PARAMS_FILENAME))
            return enums.XmlManagerReturnCodes.XML_TAG_ERROR
        
        # root_object
        try:
            json_root_object= xml_co_sim_parameters_json_file[xml_tags.CO_SIM_XML_CO_SIM_PARAMS_ROOT_OBJECT]
        except KeyError:
            self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                       xml_tags.CO_SIM_XML_CO_SIM_PARAMS_ROOT_OBJECT,
                                                                       xml_tags.CO_SIM_XML_CO_SIM_PARAMS_ROOT_OBJECT))
            return enums.XmlManagerReturnCodes.XML_TAG_ERROR

        # building the dictionary to be dumped into a file by using JSON format
        xml_json_pairs_dict = {}

        try:
            xml_json_pairs_dict = xml_co_sim_parameters_json_file[xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIRS]
        except KeyError:
            self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                       xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIRS,
                                                                       xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIRS))
            return enums.XmlManagerReturnCodes.XML_TAG_ERROR

        json_pair_dict = {}

        for key, value in xml_json_pairs_dict.items():
            current_xml_json_pair_id = key
            current_xml_json_pair_dict = value

            # json name
            try:
                json_name = current_xml_json_pair_dict[xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIR_NAME]
            except KeyError:
                self._logger.error('{},{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                              current_xml_json_pair_id,
                                                                  xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIR_NAME,
                                                                  xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIR_NAME))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # json value
            try:
                json_value = current_xml_json_pair_dict[xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIR_VALUE]
            except KeyError:
                self._logger.error('{},{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                              current_xml_json_pair_id,
                                                                   xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIR_VALUE,
                                                                   xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIR_VALUE))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # data type to be used to set the
            try:
                json_data_type = current_xml_json_pair_dict[xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIR_DATA_TYPE]
            except KeyError:
                self._logger.error('{},{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                              current_xml_json_pair_id,
                                                                   xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIR_DATA_TYPE,
                                                                   xml_tags.CO_SIM_XML_CO_SIM_PARAMS_PAIR_DATA_TYPE))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            if json_data_type == constants.CO_SIM_FLOAT_PRECISION_1:
                try:
                    json_value = float('{:.1f}'.format(float(json_value)))
                except ValueError:
                    self._logger.error('{}, for the pair {}, {} : {} a FLOAT value is expected'.format(self._xml_filename,
                                                                                                       current_xml_json_pair_id,
                                                                                                       json_name,
                                                                                                       json_value))
                    return enums.XmlManagerReturnCodes.XML_VALUE_ERROR
            elif json_data_type == constants.CO_SIM_INTEGER:
                try:
                    json_value = int(json_value)
                except ValueError:
                    self._logger.error('{}, for the pair {}, {} : {} a INTEGER value is expected'.format(self._xml_filename,
                                                                                                       current_xml_json_pair_id,
                                                                                                       json_name,
                                                                                                       json_value))
                    return enums.XmlManagerReturnCodes.XML_VALUE_ERROR
            elif json_data_type == constants.CO_SIM_STRING:
                pass # OK, the value will be taken as it is
            else:
                self._logger.error('{}, for the pair {}, {} : {} unexpected data type'.format(self._xml_filename,
                                                                                                     current_xml_json_pair_id,
                                                                                                     json_name,
                                                                                                     json_value))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            json_pair_dict[json_name] = json_value

        self.__co_simulation_parameters_for_json_dict[xml_tags.CO_SIM_XML_CO_SIM_PARAMS_JSON_FILE] = \
            {json_root_object: json_pair_dict}

        return enums.XmlManagerReturnCodes.XML_OK

    def build_particular_sections_dicts(self):
        """
            Implements the abstract method which is called at the end of the
            Co-Simulation XML file dissection process. In here it's a wrapper
            of the private method __build_action_plan_dict_from_whole_dict

        :return:
            The return code will be result provided by the private
            method __build_action_plan_dict_from_whole_dict,
            which could return the following results codes:

            XML_TAG_ERROR   -> The Co-Simulation XML file does not contain the expected TAGS
                                related to the action plan. e.g. <action_plan></action_plan>
            XML_VALUE_ERROR -> The Co-Simulation XML file does not contain the expected VALUES
                                related to the action definition itself. e.g. CO_SIM_EVENT
            XML_OK:         -> The __action_plan_dict attributed has been filled properly
        """
        self.__co_simulation_parameters_for_json_dict = {}

        return self.__build_parameters_for_json()

    def get_parameter_for_json_dict(self):
        return self.__co_simulation_parameters_for_json_dict
