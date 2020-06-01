from io import StringIO
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

from colorama import Fore
from ruamel.yaml import Node
from ruamel.yaml import RoundTripConstructor
from ruamel.yaml import YAML
# These keys are injected into the resulting dictionaries to
# preserve provenance info for the Yaml. We should switch to Ruamel which
# will support this more cleanly

START_LINE = "__line__"
END_LINE = "__endline__"
FILE = "__sourcefile__"
RAW = "__raw__"
SPAN_HINTS = {START_LINE, END_LINE, FILE, RAW}


class Span(NamedTuple):
    start_line: int  # 0 indexed
    end_line: int  # 0 indexed
    file: Optional[str]
    raw: List[str]  # all lines in the file this span is in

    context_start: int
    context_end: int

    @classmethod
    def from_dict(cls, d: Dict[str, Any], before_context=0, after_context=0) -> Optional["Span"]:  # type: ignore
        start_line = d.get(START_LINE)
        end_line = d.get(END_LINE)
        file = d.get(FILE)
        raw: List[str] = d.get(RAW)  # type: ignore

        if start_line is not None and end_line is not None:
            context_start = max(start_line - before_context, 0)
            context_end = min(end_line + after_context, len(raw))
            return Span(
                start_line,
                end_line,
                file,
                raw,
                context_start=context_start,
                context_end=context_end,
            )
        else:
            return None


DUMMY_SPAN = Span(
    start_line=0,
    end_line=0,
    file=None,
    raw=["I am a dummy span."],
    context_start=0,
    context_end=0,
)


class RuleLangError(NamedTuple):
    short_msg: str
    long_msg: Optional[str]
    level: str
    spans: List[Span]
    help: Optional[str] = None

    def __str__(self) -> str:
        return self.emit()

    @staticmethod
    def _format_line_number(span: Span, line_number: int) -> str:
        # line numbers are 0 indexed
        width = len(str(span.end_line + 1)) + 1
        base_str = str(line_number + 1)
        assert len(base_str) < width
        return base_str.ljust(width)

    def emit(self) -> str:
        header = f"{self.level}: {self.short_msg}"
        snippets = []
        for span in self.spans:
            location_hint = f"  --> {span.file}:{span.start_line + 1}"
            snippet = [location_hint]
            for line in range(span.context_start, span.context_end):
                snippet.append(
                    f"{self._format_line_number(span, line)}| {span.raw[line]}"
                )

            snippets.append("\n".join(snippet))
        snippet_str = "\n".join(snippets)
        if self.help:
            help = f"= help: {self.help}"
        else:
            help = ""
        return f"{header}\n{snippet_str}\n{Fore.BLUE}{help}{Fore.RESET}\n{Fore.RED}{self.long_msg}{Fore.RESET}\n"


def parse_yaml_with_spans(contents: str, filename: Optional[str]) -> Dict[str, Any]:
    import yaml  # here for faster startup times
    from yaml import Node
    from yaml import SafeLoader

    lines = contents.splitlines()

    class SafeLineLoader(SafeLoader):
        # NOTE! Overriding construct_sequence to add metadata doesn't work because
        # yaml will eventually do:
        # x = []; x.extend(self.construct_sequence...)

        # TODO: refactor to use ruamel
        def construct_mapping(self, node: Node, deep: bool = False) -> Dict[str, Any]:
            mapping: Dict[str, Any] = super(SafeLineLoader, self).construct_mapping(node, deep=deep)  # type: ignore
            mapping[START_LINE] = node.start_mark.line
            mapping[END_LINE] = node.end_mark.line
            mapping[FILE] = filename
            mapping[RAW] = lines
            return mapping

    parse_ruamel_spans(contents)

    return yaml.load(contents, SafeLineLoader)  # type: ignore


class Position(NamedTuple):
    line: int
    column: int

    def __repr__(self):
        return f"{self.line}:{self.column}"


class _Span(NamedTuple):
    start: Position
    end: Position

    @classmethod
    def from_node(cls, node: Node):
        start = Position(line=node.start_mark.line, column=node.start_mark.column)
        end = Position(line=node.end_mark.line, column=node.end_mark.column)
        return cls(start, end)

    def __repr__(self):
        return f"{self.start}-{self.end}"


class Located:
    def __init__(self, value: Any, span: _Span):
        self.value = value
        self.span = span

    def __eq__(self, other):
        return self.value.__eq__(other)

    def __hash__(self):
        return self.value.__hash__()

    def __repr__(self):
        return f"{self.span}: ---> {self.value}"

    def unroll(self):
        if isinstance(self.value, list):
            return [x.unroll() for x in self.value]
        elif isinstance(self.value, dict):
            return {k.unroll(): v.unroll() for k, v in self.value.items()}
        elif isinstance(self.value, Located):
            return self.value.unroll()
        else:
            return self.value


class SpanPreservingRuamelConstructor(RoundTripConstructor):

    # def construct_scalar(self, node):
    #    r = super().construct_scalar(node)
    #    return Located(r, _Span.from_node(node))

    # def construct_mapping(self, node, maptyp, deep=False):  # type: ignore
    #    r = super().construct_mapping(node, maptyp, deep)
    #    return Located(r, _Span.from_node(node))

    def construct_object(self, node, deep=False):
        r = super().construct_object(node, deep)
        return Located(r, _Span.from_node(node))


def parse_ruamel_spans(contents: str):
    yaml = YAML()
    yaml.Constructor = SpanPreservingRuamelConstructor
    data = yaml.load(StringIO(contents))
    import pdb

    pdb.set_trace()
