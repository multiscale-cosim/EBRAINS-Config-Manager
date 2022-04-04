# ------------------------------------------------------------------------------
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor
#  license agreements; and to You under the Apache License, Version 2.0. "
# ------------------------------------------------------------------------------

from __future__ import annotations
import os
from EBRAINS_ConfigManager.global_configurations_manager.xml_parsers.xml_parser import Parser
from EBRAINS_ConfigManager.global_configurations_manager.xml_parsers.config_logger import ConfigLogger
from EBRAINS_ConfigManager.global_configurations_manager.xml_parsers.directories_manager import DirectoriesManager
from EBRAINS_ConfigManager.global_configurations_manager.xml_parsers.default_directories_enum import DefaultDirectories


class ConfigurationsManager:
    
    def __init__(self) -> None:
        self.__directories_manager = DirectoriesManager()
        self.__parser = Parser()

    def setup_default_directories(self, directory) -> str:
        """Wrapper for setting up default directories"""
        # return self.__directories_manager.setup_default_directories(directory)
        return self.__directories_manager.setup_default_directories(directory)

    def make_directory(self, target_directory, parent_directory=None):
        """Wrapper for making directories"""
        if parent_directory is None:
            parent_directory = self.get_directory(DefaultDirectories.OUTPUT)
        return self.__directories_manager.make_directory(
            target_directory, parent_directory)

    def get_directory(self, directory):
        """Wrapper for retrieving directories"""
        return self.__directories_manager.get_directory(directory)

    def convert_xml_to_dictionary(self, xml):
        """Wrapper for converting xml to dictionary"""
        return self.__parser.convert_xml2dict(xml)

    def get_configuration_settings(self, component,
                                   configuration_file) -> dict:
        """Returns the configuration settings for the target component from
         the configuration_file.

        Parameters
        ----------
        component : str
            target component

        configuration_file: str
            configuration file which contains the settings for the target component

        Returns
        ------
        component_configurations_dict: dict
            configuration settings for the target component
        """
        # load xml settings for the target component
        component_configurations_xml = self.__load_xml(component,
                                                       configuration_file)
        component_configurations_dict = self.convert_xml_to_dictionary(
                                                component_configurations_xml)
        return component_configurations_dict

    def __load_xml(self, component, configuration_file):
        """helper function for getting configuration settings of a component"""
        # loads the xml configuration file as an xml.etree.ElementTree
        global_configurations_xml_tree = self.__parser.load_xml(
                                                configuration_file)
        # get root element
        root = global_configurations_xml_tree.getroot()
        # find the xml configuration settings for the desired component
        component_configurations_xml = root.find(component)
        if component_configurations_xml is None:
            raise LookupError("configuration settings not found!", component)
        return component_configurations_xml

    def load_log_configurations(self, name,
                                log_configurations,
                                target_directory=None) -> Logger:
        """
        Creates a logger with the specified name and configuration settings.
        The default location will be set for the logs if either directory or
        directory path is not specified.

        Parameters
        ----------
        name : str
            Logger name

        log_configurations: dict
            configuration settings for the logger

        target_directory: str
            target location for the logs

        Returns
        ------
        Return a logger
        """
        if target_directory is not None:
            # Case: make directory at the target location for the logs
            logs_directory = 'logs/'+name
            parent_directory =  self.get_directory(target_directory)
            logs_destination = self.make_directory(logs_directory, parent_directory)
        else:
            # Case: if no target directory is specified,
            # set the default directory for the logs
            logs_destination = self.get_directory(
                                        directory=DefaultDirectories.LOGS)
        logger = ConfigLogger()
        return logger.initialize_logger(name, logs_destination,
                                        configurations=log_configurations)
