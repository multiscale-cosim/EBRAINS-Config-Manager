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

# Co-Simulator imports
from EBRAINS_ConfigManager.workflow_configurations_manager.xml_parsers import enums
from EBRAINS_ConfigManager.workflow_configurations_manager.xml_parsers import xml_tags
from EBRAINS_ConfigManager.workflow_configurations_manager.xml_parsers import utils
from EBRAINS_ConfigManager.workflow_configurations_manager.xml_parsers import constants
from EBRAINS_Launcher.common.utils import directory_utils


class Arranger(object):
    """
        Arranges the run time environment
    """

    def __init__(self, log_settings, configurations_manager, variables_manager, items_to_be_arranged_dict):
        # getting objects referenced provided when the instance object is created
        self.__log_settings = log_settings
        self.__configurations_manager = configurations_manager
        self.__logger = self.__configurations_manager.load_log_configurations(
                                        name=__name__,
                                        log_configurations=self.__log_settings)
        self.__variables_manager = variables_manager
        self.__items_to_be_arranged_dict = items_to_be_arranged_dict

    def __dir_creation(self, dir_to_be_created):

        try:
            directory_utils.safe_makedir(dir_to_be_created)
        except Exception:
            self.__logger.error('{} making dir(s) went wrong'.format(dir_to_be_created))
            return enums.ArrangerReturnCodes.MKDIR_ERROR

        return enums.ArrangerReturnCodes.OK

    
    def __check_and_create_dir(self, directory):
        ''''checks whether the directory already exist before creating it.'''
        if not os.path.isdir(directory):
            self.__logger.debug(f'{directory} does not exist, going to create it')
            return self.__dir_creation(dir_to_be_created=directory)

    def arrange(self):
        arrangement_choices = {
            constants.CO_SIM_ARRANGEMENT_CHECK_BEFORE_CREATION: self.__check_and_create_dir,
            constants.CO_SIM_ARRANGEMENT_DIR_CREATION:self.__dir_creation
        }
            
        for key, value in self.__items_to_be_arranged_dict.items():
            # key = Arrangement XML id, e.g. arr_01
            arrangement_duty = value[xml_tags.CO_SIM_XML_ARRANGEMENT_DUTY]
            raw_arrange_what = value[xml_tags.CO_SIM_XML_ARRANGEMENT_WHAT]
            transformed_arrange_what = \
                utils.transform_co_simulation_variables_into_values(variables_manager=self.__variables_manager,
                                                                           functional_variable_value=raw_arrange_what)
            if arrangement_choices[arrangement_duty](transformed_arrange_what) ==\
                 enums.ArrangerReturnCodes.MKDIR_ERROR:
                 return enums.ArrangerReturnCodes.MKDIR_ERROR
            else:
                continue

        return enums.ArrangerReturnCodes.OK
