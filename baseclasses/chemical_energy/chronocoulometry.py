#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import numpy as np

from nomad.metainfo import (Quantity, SubSection)

from .voltammetry import Voltammetry
from .chronoamperometry import CAProperties


class CCProperties(CAProperties):

    charge_limit = Quantity(
        type=np.dtype(np.float64),
        unit=('mC'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mC'))


class Chronocoulometry(Voltammetry):

    properties = SubSection(
        section_def=CCProperties)

    def normalize(self, archive, logger):
        self.method = "Chronocoulometry"
        super(Chronocoulometry, self).normalize(archive, logger)

        if self.data_file:
            try:
                with archive.m_context.raw_file(self.data_file) as f:
                    if os.path.splitext(self.data_file)[-1] == ".DTA":
                        from ..helper.gamry_parser import get_header_and_data
                        metadata, _ = get_header_and_data(filename=f.name)

                        if "CHRONOC" in metadata["TAG"] and self.properties is None:
                            from ..helper.gamry_archive import get_cc_properties

                            properties = CCProperties()
                            get_cc_properties(metadata, properties)

                            self.properties = properties

            except Exception as e:
                logger.error(e)
        if self.properties is not None:
            if self.properties.sample_area and self.current is not None:
                self.current_density = self.current / self.properties.sample_area
            if self.properties.sample_area and self.charge is not None:
                self.charge_density = self.charge / self.properties.sample_area
