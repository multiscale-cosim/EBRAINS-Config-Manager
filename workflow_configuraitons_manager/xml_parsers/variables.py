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

#
# IMPORTANT: DO NOT FORGET TO ADD THE CO_SIM_<variable> INTO THE
#            CO_SIM_VARIABLES_TUPLE DEFINED AT THE END OF THIS FILE
#            ^^^^^^^^^^^^^^^^^^^^^^

# Co-Simulation Framework's  Environment variable
CO_SIM_ACTIONS_PATH = 'CO_SIM_ACTIONS_PATH'  # Variable name referring to the Actions XML configuration files

CO_SIM_EMPTY = 'CO_SIM_EMPTY'  # empty string shall be the assigned value
CO_SIM_EXECUTION_ENVIRONMENT = 'CO_SIM_EXECUTION_ENVIRONMENT'

CO_SIM_LAUNCHER = 'CO_SIM_LAUNCHER'  # Contains srun or mpirun according to the environment
CO_SIM_MODULES_ROOT_PATH = 'CO_SIM_MODULES_ROOT_PATH'  # mutilscale-cosim/EBRAINS-<app-domain> repos location


# The RESULTS path must be assigned on run-time gathered by means of the configuration manager
CO_SIM_RESULTS_PATH = 'CO_SIM_RESULTS_PATH'

CO_SIM_ROOT_PATH = 'CO_SIM_ROOT_PATH'  # base path to be used as reference for other location
CO_SIM_ROUTINES_PATH = 'CO_SIM_ROUTINES_PATH'  # to reference location of ROUTINES source code file

CO_SIM_PARAMETERS_PATH = 'CO_SIM_PARAMETERS_PATH'

CO_SIM_USE_CASE_ROOT_PATH = 'CO_SIM_USE_CASE_ROOT_PATH'

CO_SIM_COMMUNICATION_SETTINGS_PATH = 'CO_SIM_COMMUNICATION_SETTINGS_PATH'

CO_SIM_COMMUNICATION_SETTINGS_XML = 'CO_SIM_COMMUNICATION_SETTINGS_XML'

#
# Tuple used by the Variables Manager in order to create a dictionary for
# further processing
#
CO_SIM_VARIABLES_TUPLE = (
    CO_SIM_ACTIONS_PATH,
    CO_SIM_EMPTY,
    CO_SIM_EXECUTION_ENVIRONMENT,
    CO_SIM_LAUNCHER,
    CO_SIM_MODULES_ROOT_PATH,
    CO_SIM_PARAMETERS_PATH,
    CO_SIM_RESULTS_PATH,
    CO_SIM_ROOT_PATH,
    CO_SIM_ROUTINES_PATH,
    CO_SIM_USE_CASE_ROOT_PATH,
    CO_SIM_COMMUNICATION_SETTINGS_PATH,
    CO_SIM_COMMUNICATION_SETTINGS_XML,
)
