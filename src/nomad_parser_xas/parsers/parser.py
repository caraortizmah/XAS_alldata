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

from nomad.config import config
from nomad.parsing.parser import MatchingParser

from nomad.datamodel.metainfo.workflow import Workflow

configuration = config.get_plugin_entry_point(
    'nomad_parser_xas.parsers:parser_entry_point'
)

from nomad_simulations.schema_packages.general import Simulation
from nomad_simulations.schema_packages.general import Program
from nomad.parsing.file_parser import TextParser
from nomad.parsing.file_parser import Quantity
from nomad_simulations.schema_packages.outputs import Outputs
from nomad_simulations.schema_packages.properties import XASSpectrum
from nomad_simulations.schema_packages.properties import AbsorptionSpectrum
from nomad.metainfo import Quantity as mQuantity
import numpy as np

def states_to_dict(block):
    print('doing operation')
    return "X"

#def T_block(block):
#    return np.array(block.strip().split())

orca_out_parse = TextParser(quantities = [Quantity('version', 
                                      r'Program Version ([\d.]+)'),
                                      Quantity('state',
                                          r'(STATE +\d+ +.+?\:[\s\S]+?)\n\n', str_operation=states_to_dict, flatten=False, repeats=False),
                                      Quantity('polarization_dir',
                                          r'COMBINED ELECTRIC DIPOLE \+ MAGNETIC DIPOLE \+ ELECTRIC QUADRUPOLE SPECTRUM([\s\S]+?)\n\n', \
                                                  repeats=True, sub_parser=TextParser(quantities = [Quantity('data_block',
                                                      r'(\d+ \d.+)', repeats=True)]))
                            ])

class ROCISDFT_xas(AbsorptionSpectrum):
    """ """

    # ! implement `iri` and `rank` as part of `m_def = Section()`

    orca_fosc_dmq = mQuantity(
        type=float,
        shape=['*'],
        description="""
        Taking the COMBINED ELECTRIC DIPOLE + MAGNETIC DIPOLE + ELECTRIC QUADRUPOLE SPECTRUM
        """,
    )

class ORCANewParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        print('ROCIS/DFT!\n')
        simulation = Simulation()

        orca_out_parse.mainfile = mainfile
        
        dmq = np.array(orca_out_parse.polarization_dir[0].data_block)


        program = Program(name='orca',
                version=orca_out_parse.get('version'))
        simulation.program = program
        simulation.outputs = [Outputs(xas_spectra=[XASSpectrum(xanes_spectrum=ROCISDFT_xas(orca_fosc_dmq=dmq.T[6]))])]
        archive.data = simulation
        #archive.workflow2 = Workflow(name='test')
