from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class NewParserEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad_parser_xas.parsers.parser import ORCANewParser

        return ORCANewParser(**self.dict())


parser_entry_point = NewParserEntryPoint(
    name='ORCANewParser',
    description='New parser entry point configuration.',
    mainfile_contents_re=r'12345\_',
)
