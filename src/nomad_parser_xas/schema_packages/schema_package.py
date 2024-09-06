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
from nomad.datamodel.data import Schema, ArchiveSection
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.metainfo import Quantity as mQuantity, SchemaPackage, SubSection
from nomad_simulations.schema_packages.properties.spectral_profile import XASSpectrum

configuration = config.get_plugin_entry_point(
    'nomad_parser_xas.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()

class ROCISDFT_xas_state(ArchiveSection):
    occupied = mQuantity(
        type=np.int32,
        shape=['*'],
        description="""
        Index of the occupied molecular orbital from a resonant transition
        """,
    )

    virtual = mQuantity(
        type=np.int32,
        shape=['*'],
        description="""
        Index of the virtual molecular orbital from a resonant transition
        """,
    )

    trans_prob = mQuantity(
        type=np.float64,
        shape=['*'],
        description="""
        Transition probability of the occupied-virtual molecular orbital coupling
        """,
    )

    trans_amp = mQuantity(
        type=np.float64,
        shape=['*'],
        description="""
        Transition amplitude of the occupied-virtual molecular orbital coupling
        """,
    )


class ROCISDFT_xas(XASSpectrum):
    """ """

    orca_fosc_dmq = mQuantity(
        type=np.float64,
        shape=['*'],
        description="""
        Taking the COMBINED ELECTRIC DIPOLE + MAGNETIC DIPOLE + ELECTRIC QUADRUPOLE SPECTRUM (origin adjusted)
        """,
    )

    orca_state = SubSection(sub_section=ROCISDFT_xas_state.m_def, repeats=True, description='')


m_package.__init_metainfo__()
