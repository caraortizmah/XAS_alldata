from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

import numpy as np

from nomad.config import config
from nomad.datamodel.data import Schema
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.metainfo import Quantity as mQuantity, SchemaPackage
from nomad_simulations.schema_packages.properties.spectral_profile import XASSpectrum

configuration = config.get_plugin_entry_point(
    'nomad_parser_xas.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()


class ROCISDFT_xas(XASSpectrum):
    """ """

    orca_fosc_dmq = mQuantity(
        type=np.float64,
        shape=['*'],
        description="""
        Taking the COMBINED ELECTRIC DIPOLE + MAGNETIC DIPOLE + ELECTRIC QUADRUPOLE SPECTRUM (origin adjusted)
        """,
    )

    orca_state = mQuantity(
        type=np.float64,
        shape=['*'],
        description="""
        Taking the excited states from Eigenvectors of ROCIS calculation:
        """,
    )


m_package.__init_metainfo__()
