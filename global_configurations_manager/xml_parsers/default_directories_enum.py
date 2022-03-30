# ------------------------------------------------------------------------------
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor
#  license agreements; and to You under the Apache License, Version 2.0. "
# ------------------------------------------------------------------------------
import enum


@enum.unique
class DefaultDirectories(enum.Enum):
    """ Enum class for default directories """

    OUTPUT = 'output'
    SIMULATION_RESULTS = 'simulation_results'
    LOGS = 'logs'
    MONITORING_DATA = 'monitoring_data'
