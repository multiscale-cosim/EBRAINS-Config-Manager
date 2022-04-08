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

# Co-Simulator Imports
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import enums
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import variables
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import constants
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import exceptions
from EBRAINS_ConfigManager.workflow_configuraitons_manager.xml_parsers import utils


class VariablesManager(object):
    """
        Manages the variables related to the run-time environment
    """
    __logger = None

    def __init__(self, log_settings, configurations_manager):
        self.__log_settings = log_settings
        self.__configurations_manager = configurations_manager
        self.__logger = self.__configurations_manager.load_log_configurations(
                                        name=__name__,
                                        log_configurations=self.__log_settings)

        self.__dict = {
            # Actions XML files location
            variables.CO_SIM_ACTIONS_DIR: {
                constants.CO_SIM_VARIABLE_DESCRIPTION: 'Path to actions XML files',
                constants.CO_SIM_VARIABLE_VALUE: None},
            # Empty, TO BE USED AS A FAKE VALUE
            variables.CO_SIM_EMPTY: {
                constants.CO_SIM_VARIABLE_DESCRIPTION: 'empty string',
                constants.CO_SIM_VARIABLE_VALUE: ''},
            # Execution Environment <Local|Cluster>
            variables.CO_SIM_EXECUTION_ENVIRONMENT: {
                constants.CO_SIM_VARIABLE_DESCRIPTION: 'Co-Simulator Execution Environment',
                constants.CO_SIM_VARIABLE_VALUE: None},
            # Results Output Directory
            variables.CO_SIM_RESULTS_DIR: {
                constants.CO_SIM_VARIABLE_DESCRIPTION: 'Results files directory location',
                constants.CO_SIM_VARIABLE_VALUE: None},
            # Routines Directory Path
            variables.CO_SIM_ROUTINES_DIR: {
                constants.CO_SIM_VARIABLE_DESCRIPTION: 'Co-Simulation Routines directory location',
                constants.CO_SIM_VARIABLE_VALUE: None},
        }

    def get_value(self, variable_name):
        """
        :param variable_name: The environment variable name which the value is being gotten (requested)
        :return: The value of the passed variable name
        """
        return self.__dict[variable_name][constants.CO_SIM_VARIABLE_VALUE]

    def set_value(self, variable_name, variable_value):
        """

        :param variable_value:
        :param variable_name:
        :return:
        """
        try:
            self.__dict[variable_name][constants.CO_SIM_VARIABLE_VALUE] = variable_value
        except KeyError:
            # TODO handle exception here
            self.__logger.error('{} has not been declared in the variable manager yet'.format(variable_name))
            raise exceptions.CoSimVariableNotFound(co_sim_variable_name=variable_name)

        return self.__dict[variable_name]

    def set_co_sim_variable_values_from_variables_dict(self, variables_dictionary_source):
        """

        :param variables_dictionary_source: Dictionary containing Co-Simulation Variables (CO_SIM_*)
        :return:

        """
        for key, value in variables_dictionary_source.items():
            try:
                self.__dict[key][constants.CO_SIM_VARIABLE_VALUE] = value
            except KeyError:
                self.__logger.error('{} is not a defined Co-Simulator variable'.format(key))
                return enums.VariablesReturnCodes.VARIABLE_NOT_OK

        return enums.VariablesReturnCodes.VARIABLE_OK

    def create_variables_from_parameters_dict(self, input_dictionary):
        """
            Transforms the referenced variables names into its values based on CO_SIM_* variables.

            CO_SIM_* variables are those referencing a value in the same XML configuration file.
                e.g.
                    CO_SIM_RUNTIME_RESULTS_DIR -> represents the output path where the results files
                                                    will be written/read.
                    and could be referenced as follows:
                    <var_186>
                        <var_name>CO_SIM_VISUALIZATION_FILES_OUTPUT_PATH</var_name>
                        <var_value>CO_SIM_RUNTIME_RESULTS_DIR/visualizer</var_value>
                    </var_186>

            Environment variables are those defined on the system where the Co-Simulation process is being run.
                e.g.
                        ${CO_SIM_TVB_NEST_PATH} -> represents the path where the TVB_NEST repository is located.
                    and could be referenced as follows:
                    <var_194>
                        <var_name>CO_SIM_XML_ACTIONS_DIR</var_name>
                        <var_value>${CO_SIM_TVB_NEST_PATH}/co_simulator/actions</var_value>
                    </var_194>

        :param input_dictionary:
            The private attribute object reference of the dictionary where the
            variables will be transformed into its values

        :return:
            XML_OK: All the referenced variables in the dictionary where properly
                    interchanged by its values
            XML_CO_SIM_VARIABLE_ERROR: The value for a referenced variable could not been obtained
        """
        for key, value in input_dictionary.items():
            # transforming the CO_SIM_ references into its values
            try:
                runtime_variable_value = \
                    utils.transform_co_simulation_variables_into_values(variables_manager=self,
                                                                               functional_variable_value=value)
            except exceptions.CoSimVariableNotFound as CoSimVariableNotFound:
                self.__logger.error(CoSimVariableNotFound)
                # return enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR
                return enums.ParametersReturnCodes.VARIABLE_NOT_FOUND

            # creating the new CO_SIM_ variable
            self.__dict[key] = {constants.CO_SIM_VARIABLE_DESCRIPTION: 'created on run time',
                                constants.CO_SIM_VARIABLE_VALUE: runtime_variable_value}
        return enums.ParametersReturnCodes.PARAMETER_OK

    def create_co_sim_run_time_variables(self, action_plan_variables_dict=None, action_plan_parameters_dict=None):
        """
            Sets RUN TIME Co-Simulation variables based on the content of the variables
            and parameters set on the Action Plan XML file

        :return:
            VARIABLE_OK
        """
        # CO_SIM_LAUNCHER
        try:
            execution_environment = \
                self.__dict[variables.CO_SIM_EXECUTION_ENVIRONMENT][constants.CO_SIM_VARIABLE_VALUE]
        except KeyError:
            self.__logger.error('{} has not been set yet'.format(variables.CO_SIM_EXECUTION_ENVIRONMENT))
            return enums.VariablesReturnCodes.VARIABLE_NOT_OK
        else:
            if execution_environment.upper() == 'LOCAL':
                self.__dict[variables.CO_SIM_LAUNCHER] = \
                    {constants.CO_SIM_VARIABLE_DESCRIPTION: 'launcher created on run time',
                     constants.CO_SIM_VARIABLE_VALUE: 'mpirun'}
            elif execution_environment.upper() == 'CLUSTER':
                self.__dict[variables.CO_SIM_LAUNCHER] = \
                    {constants.CO_SIM_VARIABLE_DESCRIPTION: 'launcher created on run time',
                     constants.CO_SIM_VARIABLE_VALUE: 'srun'}
            else:
                self.__logger.error('{} wrong value set. <LOCAL|CLUSTER>'.format(
                    variables.CO_SIM_EXECUTION_ENVIRONMENT))
                return enums.VariablesReturnCodes.VARIABLE_NOT_OK

        return enums.VariablesReturnCodes.VARIABLE_OK
