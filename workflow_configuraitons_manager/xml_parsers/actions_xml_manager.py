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
import os

# Co-Simulator's imports
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import constants
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import exceptions
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import enums
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import utils
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import variables
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import xml_tags

from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers.xml_manager import XmlManager


class ActionsXmlManager(object):
    """
        XML Manager for the Co-Simulation Actions XML files

        NOTE: This class mimic the behaviour of the XmlManager,
                nevertheless, goes through the actions dictionary
                and each entry in the dictionary is processed
                with the XMLManager subclass __CoSimulationActionXmlManager

        IMPORTANT: __CoSimulationActionXmlManager processes each XML Action particularly

    """
    __sci_params_xml_path_filenames_dict = {}
    __actions_popen_arguments_dict = {}

    def __init__(self, log_settings, configurations_manager, variables_manager, action_plan, ):
        self.__log_settings = log_settings
        self.__configurations_manager = configurations_manager
        self.__logger = self.__configurations_manager.load_log_configurations(
            name=__name__,
            log_configurations=self.__log_settings)
        self.__variables_manager = variables_manager
        self.__action_plan = action_plan

    def __transform_path_co_sim_variables_into_values(self, path=''):
        try:
            transformed_path = \
                utils.transform_co_simulation_variables_into_values(variables_manager=self.__variables_manager,
                                                                    functional_variable_value=path)
        # except KeyError:
        #     self.__logger.error('{} references to a CO_SIM_ variable not have been set yet'.format(item))
        #     return enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR
        except exceptions.CoSimVariableNotFound:
            self.__logger.error(
                '{} is being referenced, nevertheless the variable has not been set yet'.format(path))
            return enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR, None

        return enums.XmlManagerReturnCodes.XML_OK, transformed_path

    def __transform_popen_args_co_sim_variables_into_values(self, popen_arguments_list=None):
        """
            Goes through the elements in the Popen arguments list to find references to the CO_SIM_* variables,
            and transform them into the run time values

        :return:
            XML_OK: All the CO_SIM_* variables references were transformed into the corresponding run time values
        """
        for index, item in enumerate(popen_arguments_list):
            try:
                popen_arguments_list[index] = \
                    utils.transform_co_simulation_variables_into_values(variables_manager=self.__variables_manager,
                                                                        functional_variable_value=item)
            # except KeyError:
            #     self.__logger.error('{} references to a CO_SIM_ variable not have been set yet'.format(item))
            #     return enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR
            except exceptions.CoSimVariableNotFound:
                self.__logger.error(
                    '{} is being referenced, nevertheless the variable has not been set yet'.format(item))
                return enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR

        # Removing those items with empty value, i.e. equal to ''
        if self.__variables_manager.get_value(variable_name=variables.CO_SIM_EMPTY) in popen_arguments_list:
            popen_arguments_list.remove(self.__variables_manager.get_value(variable_name=variables.CO_SIM_EMPTY))

        return enums.XmlManagerReturnCodes.XML_OK

    def dissect(self):
        """
            Takes each XML action file reference in the XML action plan configuration file
            and dissect them by using the nested Action XML Manager subclass

        :return:
            XML_CO_SIM_VARIABLE_ERROR: At least a CO_SIM_* variable is not managed by the
            XML_OK: All actions XML files were processed correctly
        """
        actions_xml_file_location = \
            self.__variables_manager.get_value(variables.CO_SIM_ACTIONS_PATH)

        for key, value in self.__action_plan.items():
            # key = action_NNN <- the identification in the action plan
            if value[xml_tags.CO_SIM_XML_PLAN_ACTION_TYPE] == constants.CO_SIM_ACTION:
                # taking into account only actions (scripts or binaries) able to be executed

                # current_action_id = key  # action_NNN
                current_action_xml_path_filename = os.sep.join([actions_xml_file_location,
                                                                value[xml_tags.CO_SIM_XML_PLAN_ACTION_XML],
                                                                ])

                xml_action_manager = self._CoSimulationActionXmlManager(
                    log_settings=self.__log_settings,
                    configurations_manager=self.__configurations_manager,
                    xml_filename=current_action_xml_path_filename,
                    name='ActionXmlManager')

                # Splitting the XML dictionary into dictionaries by XML section
                # At the end of the dissection process,
                # there will be an attribute (list) with the Popen arguments
                dissect_return = xml_action_manager.dissect()

                if not dissect_return == enums.XmlManagerReturnCodes.XML_OK:
                    self.__logger.error('Error found dissecting {}'.format(current_action_xml_path_filename))
                    return dissect_return

                # Post-processing steps
                # raw values gathered from XML configuration file, they will be transformed into run-time values

                # STEP 1 - Scientific Parameters path+filename
                sci_params_xml_path_filename = xml_action_manager.get_sci_params_xml_path_filename()

                return_value, transformed_path_filename = self.__transform_path_co_sim_variables_into_values(
                    path=sci_params_xml_path_filename)
                if not return_value == enums.XmlManagerReturnCodes.XML_OK:
                    self.__logger.error(
                        'Error found transforming into values the CO_SIM_ variables found in {}'.format(
                            sci_params_xml_path_filename))
                    return enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR

                self.__sci_params_xml_path_filenames_dict[key] = transformed_path_filename

                # STEP 2 - Popen arguments list
                # Command-line argv[0..n] for Popen call, including mpirun (local VMs) srun (HPC)
                popen_arguments_list = xml_action_manager.get_popen_arguments_list()
                # transform CO_SIM_* variables
                # NOTE: the CO_SIM_* variables must have the run-time values assigned in this point,
                # otherwise, the Co-Simulation process will not be performed properly
                if not self.__transform_popen_args_co_sim_variables_into_values(
                        popen_arguments_list=popen_arguments_list) == enums.XmlManagerReturnCodes.XML_OK:
                    self.__logger.error(
                        'Error found transforming into values the CO_SIM_ variables found in {}'.format(
                            current_action_xml_path_filename))
                    return enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR
                self.__actions_popen_arguments_dict[key] = popen_arguments_list

        return enums.XmlManagerReturnCodes.XML_OK

    def get_actions_popen_arguments_dict(self):
        """

        :return:
            Dictionary containing the popen argument list keyed by action identification in the action plan
        """
        return self.__actions_popen_arguments_dict

    def get_actions_sci_params_xml_files_dict(self):
        """

        :return:
            Dictionary containing the XML PATH+FILENAME of the Scientific Parameters by Action ID
        """
        return self.__sci_params_xml_path_filenames_dict

    class _CoSimulationActionXmlManager(XmlManager):
        """
            XML Manager for the Co-Simulation Actions XML files
        """

        __performer_dict = {}
        __Popen_arguments_list = []

        __sci_params_xml_path_filename = None

        def initialize_xml_elements(self):
            # TO BE DONE: there should be a global XML file where tags are defined
            self._component_xml_tag = xml_tags.CO_SIM_XML_ACTION_ROOT_TAG

        def __dissect_variables_section(self):
            """
                Getting references to CO_SIM_* variables declared on the Action XML configuration files

            :return:
                XML_TAG_ERROR: A tag was not found by dissecting the <variables> section
                XML_OK: The <variables> section parsing process was successful.
            """

            return enums.XmlManagerReturnCodes.XML_OK

        def __dissect_parameters_section(self):
            """
                Getting references to the functional and scientific parameters XML configuration files

            :return:
                XML_TAG_ERROR: A tag was not found by dissecting the <parameters> section
                XML_OK: The <parameters> section parsing process was successful.
            """

            try:
                self.__sci_params_xml_path_filename = self.get_parameters_dict()[constants.CO_SIM_SCIENTIFIC_PARAMETERS]
            except KeyError:
                self.__sci_params_xml_path_filename = None  # The XML action file does not contain scientific parameters
                self._logger.error('{} has no defined'.format(self._xml_filename,
                                                              constants.CO_SIM_SCIENTIFIC_PARAMETERS))

                # it is not considered an error since an action could perform another kind of task than scientific

            return enums.XmlManagerReturnCodes.XML_OK

        def __dissect_launcher_section(self):
            """
                Fills the Popen list from the launcher section
            :return:
                XML_TAG_ERROR: Error found dissecting the launcher section of the action section
                XML_OK: The launcher section was dumped properly into the Popen arguments list
            """
            # launcher binary, e.g. mpirun or slurm
            try:
                self.__Popen_arguments_list.append(
                    self.__launcher_dict[xml_tags.CO_SIM_XML_ACTION_LAUNCHER_COMMAND])
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION_LAUNCHER_COMMAND,
                                                                           xml_tags.CO_SIM_XML_ACTION_LAUNCHER_COMMAND))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # arguments for the launcher binary
            try:
                launcher_arguments_dict = self.__launcher_dict[xml_tags.CO_SIM_XML_ACTION_LAUNCHER_ARGUMENTS]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION_LAUNCHER_ARGUMENTS,
                                                                           xml_tags.CO_SIM_XML_ACTION_LAUNCHER_ARGUMENTS))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            for key, value in launcher_arguments_dict.items():
                # key = argv_NN -> Argument identification
                self.__Popen_arguments_list.append(value)

            return enums.XmlManagerReturnCodes.XML_OK

        def __dissect_performer_section(self):
            """
                Fills the Popen list from the performer section
            :return:
                XML_TAG_ERROR: Error found dissecting the performer section of the action section
                XML_OK: The performer section was dumped properly into the Popen arguments list
            """
            # performer binary, e.g. python3
            try:
                self.__Popen_arguments_list.append(
                    self.__performer_dict[xml_tags.CO_SIM_XML_ACTION_PERFORMER_BINARY])
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION_PERFORMER_BINARY,
                                                                           xml_tags.CO_SIM_XML_ACTION_PERFORMER_BINARY))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # arguments for the performer binary
            try:
                performer_arguments_dict = self.__performer_dict[xml_tags.CO_SIM_XML_ACTION_PERFORMER_ARGUMENTS]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION_PERFORMER_ARGUMENTS,
                                                                           xml_tags.CO_SIM_XML_ACTION_PERFORMER_ARGUMENTS))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            for key, value in performer_arguments_dict.items():
                # key = argv_NN -> Argument identification
                self.__Popen_arguments_list.append(value)

            return enums.XmlManagerReturnCodes.XML_OK

        def __dissect_routine_section(self):
            """
                Fills the Popen list from the routine section
            :return:
                XML_TAG_ERROR: Error found dissecting the routine section of the action section
                XML_OK: The routine section was dumped properly into the Popen arguments list
            """
            # script/binary which performs the science/transformation/simulation procedure/workflow
            try:
                self.__Popen_arguments_list.append(
                    self.__routine_dict[xml_tags.CO_SIM_XML_ACTION_ROUTINE_CODE])
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION_ROUTINE_CODE,
                                                                           xml_tags.CO_SIM_XML_ACTION_ROUTINE_CODE))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # arguments for the routine script/binary
            try:
                routine_arguments_dict = self.__routine_dict[xml_tags.CO_SIM_XML_ACTION_ROUTINE_ARGUMENTS]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION_ROUTINE_ARGUMENTS,
                                                                           xml_tags.CO_SIM_XML_ACTION_ROUTINE_ARGUMENTS))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            for key, value in routine_arguments_dict.items():
                # key = argv_NN -> Argument identification
                self.__Popen_arguments_list.append(value)

            return enums.XmlManagerReturnCodes.XML_OK

        def __dissect_xml_action_sections(self):
            """
                Takes the whole dictionary representing the whole action XML file,
                and extract the content from the <action> section

            :return:

                XML_OK: the Popen argument list was built properly
            """
            xml_action_dict = {}

            try:
                xml_action_dict = self._main_xml_sections_dicts_dict[xml_tags.CO_SIM_XML_ACTION]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION,
                                                                           xml_tags.CO_SIM_XML_ACTION))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # launcher, i.e. mpirun or slurm
            try:
                self.__launcher_dict = xml_action_dict[xml_tags.CO_SIM_XML_ACTION_LAUNCHER]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION_LAUNCHER,
                                                                           xml_tags.CO_SIM_XML_ACTION_LAUNCHER))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            if not self.__dissect_launcher_section() == enums.XmlManagerReturnCodes.XML_OK:
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # performer, i.e. python3 or EMPTY
            # TO BE DONE: check when a binary is referenced and a performer (interpreter) is not required
            try:
                self.__performer_dict = xml_action_dict[xml_tags.CO_SIM_XML_ACTION_PERFORMER]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION_PERFORMER,
                                                                           xml_tags.CO_SIM_XML_ACTION_PERFORMER))
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            if not self.__dissect_performer_section() == enums.XmlManagerReturnCodes.XML_OK:
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # the routine per se, i.e. a script interpreted by the performer or a binary
            try:
                self.__routine_dict = xml_action_dict[xml_tags.CO_SIM_XML_ACTION_ROUTINE]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           xml_tags.CO_SIM_XML_ACTION_ROUTINE,
                                                                           xml_tags.CO_SIM_XML_ACTION_ROUTINE))

            if not self.__dissect_routine_section() == enums.XmlManagerReturnCodes.XML_OK:
                return enums.XmlManagerReturnCodes.XML_TAG_ERROR

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
            # file containing the science parameters used to configure the simulation model
            self.__sci_params_xml_path_filename = None

            # list of arguments to be used when Popen is called
            self.__Popen_arguments_list = []

            # STEP 1 - <variables></variables>
            return_value = self.__dissect_variables_section()
            if not return_value == enums.XmlManagerReturnCodes.XML_OK:
                return return_value

            # STEP 2 - <parameters></parameters> - functional and scientific
            return_value = self.__dissect_parameters_section()
            if not return_value == enums.XmlManagerReturnCodes.XML_OK:
                return return_value

            # STEP 3 - <action></action> -> Popen arguments list
            return self.__dissect_xml_action_sections()

        def get_sci_params_xml_path_filename(self):
            return self.__sci_params_xml_path_filename

        def get_popen_arguments_list(self):
            return self.__Popen_arguments_list
