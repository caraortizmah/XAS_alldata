from typing import (
    TYPE_CHECKING, Optional, Union
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

import re

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
from nomad_parser_xas.schema_packages.schema_package import ROCISDFT_xas
import numpy as np


re_float = '-?\d+\.\d+'

def states_to_dict(text_block: str) -> Optional[dict[str, list[Union[int, float]]]]:
    re_line = rf'(\d+)->(\d+)\s+:\s+{re_float}\s+\(({re_float})\)'
    blocks = [re.search(re_line, line).group(0) for line in text_block.strip().split('\n')]

    reshaped: dict[str, list[Union[int, float]]] = {'occ': [], 'virt': [], 'prob': [], 'amp': []}
    for block in blocks:
        reshaped['occ'].append = block[0]
        reshaped['virt'].append = block[1]
        reshaped['prob'].append = block[2]
        reshaped['amp'].append = block[3]

    return reshaped

# def T_block(block):
#    return np.array(block.strip().split())

orca_out_parse = TextParser(
    quantities=[
        Quantity('version', r'Program Version ([\d.]+)'),
        Quantity(
            'states',
            r'(STATE +\d+ +.+?\:[\s\S]+?)\n\n',
            flatten=False,
            repeats=True,
            sub_parser=TextParser(
                quantities=[
                    Quantity(
                        'data_bystate',
                        r'\d+cm\*\*-1\n([\s\S]+?)\n\n',
                        str_operation=states_to_dict,
                    )
                ],
            ),
        ),
        Quantity(
            'polarization_totaldir',
            r'COMBINED ELECTRIC DIPOLE \+ MAGNETIC DIPOLE \+ ELECTRIC QUADRUPOLE SPECTRUM \(origin adjusted\)([\s\S]+?)\n\n',
            repeats=True,
            sub_parser=TextParser(
                quantities=[Quantity('data_block', r'(\d+ \d.+)', repeats=True)]
            ),
        ),
    ]
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

        setstates = np.array(orca_out_parse.states[0].data_bystate)

        dmq = np.array(orca_out_parse.polarization_totaldir[0].data_block)

        program = Program(name='orca', version=orca_out_parse.get('version'))
        simulation.program = program
        simulation.outputs = [
            Outputs(
                xas_spectra=[
                    ROCISDFT_xas(orca_fosc_dmq=dmq.T[[1, 6]], orca_state=setstates)
                ]
            )
        ]
        archive.data = simulation
        # archive.workflow2 = Workflow(name='test')
