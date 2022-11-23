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
import re

# Co-Simulator Imports
from EBRAINS_ConfigManager.workflow_configurations_manager.xml_parsers import enums
from EBRAINS_ConfigManager.workflow_configurations_manager.xml_parsers import variables
from EBRAINS_ConfigManager.workflow_configurations_manager.xml_parsers import constants
from EBRAINS_ConfigManager.workflow_configurations_manager.xml_parsers import exceptions
from EBRAINS_ConfigManager.workflow_configurations_manager.xml_parsers import utils


class VariablesManager(object):
    """
        Manages the variables related to the run-time environment
    """
    __logger = None
    __dict = {}

    def __init__(self, log_settings, configurations_manager):
        self.__log_settings = log_settings
        self.__configurations_manager = configurations_manager
        self.__logger = self.__configurations_manager.load_log_configurations(
            name=__name__,
            log_configurations=self.__log_settings)

        for curr_co_sim_variable in variables.CO_SIM_VARIABLES_TUPLE:
            self.__dict.update({curr_co_sim_variable: {constants.CO_SIM_VARIABLE_DESCRIPTION: '',
                                                       constants.CO_SIM_VARIABLE_VALUE: None}})

        # CO_SIM_EMPTY is used as a "None" value for CO_SIM_<variable>,
        # hence an EMPTY string is assigned as a value to it
        self.__dict.update({'CO_SIM_EMPTY': {constants.CO_SIM_VARIABLE_DESCRIPTION: '',
                                             constants.CO_SIM_VARIABLE_VALUE: ''}})

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

            # In this point, key is a recognized (defined) CO_SIM_ variable
            # hence, the value to assigned to it could be another CO_SIM variable
            # IMPORTANT: The order how the CO_SIM variables are referenced is relevant
            #            for the proper processing (conversion into values).
            run_time_value = utils.transform_co_simulation_variables_into_values(variables_manager=self,
                                                                                 functional_variable_value=value)
            self.__dict[key][constants.CO_SIM_VARIABLE_VALUE] = run_time_value

        return enums.VariablesReturnCodes.VARIABLE_OK

    def create_variables_from_parameters_dict(self, input_dictionary):
        """
            Transforms the referenced variables names into its values based on CO_SIM_* variables.

            CO_SIM_* variables are those referencing a value in the same XML configuration file.
                e.g.
                    CO_SIM_RUNTIME_RESULTS_PATH -> represents the output path where the results files
                                                    will be written/read.
                    and could be referenced as follows:
                    <var_186>
                        <var_name>CO_SIM_VISUALIZATION_FILES_OUTPUT_PATH</var_name>
                        <var_value>CO_SIM_RUNTIME_RESULTS_PATH/visualizer</var_value>
                    </var_186>

            Environment variables are those defined on the system where the Co-Simulation process is being run.
                e.g.
                        ${CO_SIM_TVB_NEST_PATH} -> represents the path where the TVB_NEST repository is located.
                    and could be referenced as follows:
                    <var_194>
                        <var_name>CO_SIM_XML_ACTIONS_PATH</var_name>
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

    def create_co_sim_run_time_variables(self):
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

                # In this point of execution, it is clear that the run-time environment is a HPC cluster,
                #  assumed that the SLURM's resources have been allocated by means
                # of salloc

                return self.__creates_co_sim_vars_from_slurm_env_vars()
            else:
                self.__logger.error('{} wrong value set. <LOCAL|CLUSTER>'.format(
                    variables.CO_SIM_EXECUTION_ENVIRONMENT))
                return enums.VariablesReturnCodes.VARIABLE_NOT_OK

        return enums.VariablesReturnCodes.VARIABLE_OK

    def __creates_co_sim_vars_from_slurm_env_vars(self):
        """
            Populates the CO_SIM_* variables from the SLURM_* environment variables
            IMPORTANT: It is assumed that salloc has been executed and the resources
                        haven assigned properly (end-user task)
        :return
            VARIABLE_OK
            VARIABLE_NOT_OK
        """

        # No. of requested HPC nodes
        try:
            n_nodes = int(os.environ['SLURM_NNODES'])
            self.__dict[variables.CO_SIM_SLURM_NNODES] = \
                {constants.CO_SIM_VARIABLE_DESCRIPTION: 'SLURM_NNODES',
                 constants.CO_SIM_VARIABLE_VALUE: n_nodes}
        except KeyError:
            self.__logger.error('SLURM_NNODES environment variable has not been set yet, use "salloc"')
            return enums.VariablesReturnCodes.VARIABLE_NOT_FOUND

        # Since SLURM_NNODES is set, meaning SLURM_NODELIST must be set as well,
        # e.g. SLURM_NODELIST=jsfc056       -> 1 Node
        #      SLURM_NODELIST=jsfc[056-057] -> 2 Nodes
        slurm_node_list_prefix_and_range = re.split('\[|\]', os.environ['SLURM_NODELIST'])
        node_range_length = len(slurm_node_list_prefix_and_range)
        if 0 == node_range_length:
            self.__logger.error('SLURM_NODELIST environment variable has not been set yet, use "salloc"')
            return enums.VariablesReturnCodes.VALUE_NOT_SET
        elif 1 == node_range_length and node_range_length != n_nodes:
            # There is no match between SLURM_NNODES and SLURM_NODELIST
            self.__logger.error('SLURM_NODELIST does not match with SLURM_NODELIST, it might be "salloc" failed')
            return enums.VariablesReturnCodes.VARIABLE_NOT_OK
        elif 1 == node_range_length:
            # only one HPC node is being used
            #
            # This is a wrong assigment: self.__dict['CO_SIM_SLURM_NODE_000'] = slurm_node_list_prefix_and_range[0]
            #
            self.__dict['CO_SIM_SLURM_NODE_000'] = \
                {constants.CO_SIM_VARIABLE_DESCRIPTION: 'SLURM compute node hostname',
                 constants.CO_SIM_VARIABLE_VALUE: slurm_node_list_prefix_and_range[0] }
        else:
            # two or more HPC nodes have been allocated
            hpc_nodes_name_prefix = slurm_node_list_prefix_and_range[0]
            hpc_nodes_name_range = slurm_node_list_prefix_and_range[1]
            nodes_name_suffix_list = re.split(r'-', hpc_nodes_name_range)
            first_node_name_suffix = nodes_name_suffix_list[0]
            last_node_name_suffix = nodes_name_suffix_list[1]

            n_correlative = 0
            for curr_n_node_name_suffix in range(int(first_node_name_suffix), int(last_node_name_suffix) + 1):
                co_sim_slurm_node_variable_name = f'CO_SIM_SLURM_NODE_{n_correlative:0>3d}'

                self.__dict[co_sim_slurm_node_variable_name] = \
                    {constants.CO_SIM_VARIABLE_DESCRIPTION: f'SLURM compute node hostname {n_correlative:0>3d}',
                     constants.CO_SIM_VARIABLE_VALUE: f'{hpc_nodes_name_prefix}{curr_n_node_name_suffix:0>3d}'}

                n_correlative += 1

        return enums.VariablesReturnCodes.VARIABLE_OK