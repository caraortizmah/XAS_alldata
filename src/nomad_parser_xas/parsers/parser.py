from typing import TYPE_CHECKING, Optional, Union

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
from nomad_parser_xas.schema_packages.schema_package import ROCISDFT_xas, ROCISDFT_xas_state
import numpy as np


re_float = '-?\d+\.\d+'

# def T_block(block):
#    return np.array(block.strip().split())

orca_out_parse = TextParser(
    quantities=[
        Quantity('version', r'Program Version ([\d.]+)'),
        Quantity(
            'states',
            r'(STATE +\d+ +.+?\:[\s\S]+?)\n\n',
            repeats=True,
            sub_parser=TextParser(
                quantities=[
                    Quantity(
                        'data_by_state',
                        rf'(\d+)->(\d+)\s+:\s+({re_float})\s+\(({re_float})\)',
                        repeats=True,
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

        setstates: list[ROCISDFT_xas_state] = []
        for state in orca_out_parse.states:
            if (data_by_state := state.get('data_by_state')) is not None:
                data_by_state = np.array(data_by_state).T
                setstates.append(
                    ROCISDFT_xas_state(
                        occupied=data_by_state[0],
                        virtual=data_by_state[1],
                        trans_prob=data_by_state[2],
                        trans_amp=data_by_state[3],
                    )
                )

        # dmq = np.array(orca_out_parse.polarization_totaldir[0].data_block)

        program = Program(name='orca', version=orca_out_parse.get('version'))
        simulation.program = program
        simulation.outputs = [
            Outputs(
                xas_spectra=[
                    ROCISDFT_xas(orca_state=setstates)
                ]
            )
        ]
        archive.data = simulation
        # archive.workflow2 = Workflow(name='test')
