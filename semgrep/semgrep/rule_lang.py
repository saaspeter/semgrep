import hashlib
from io import StringIO
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import NewType
from typing import Optional
from typing import Union

from ruamel.yaml import Node
from ruamel.yaml import RoundTripConstructor
from ruamel.yaml import YAML

SourceFileHash = NewType("SourceFileHash", str)


class SpanBuilder:
    """
    Singleton class tracking mapping from filehashes -> file contents to support
    building error messages from Spans
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpanBuilder, cls).__new__(cls)
            cls._instance.sources = {}
            # Put any initialization here.
        return cls._instance

    def add_source(self, file_hash: SourceFileHash, source: str):
        self.sources[file_hash] = source


def src_to_hash(contents: Union[str, bytes]) -> SourceFileHash:
    if isinstance(contents, str):
        contents = contents.encode("utf-8")
    return SourceFileHash(hashlib.sha256(contents).hexdigest())


class Position(NamedTuple):
    line: int
    column: int

    def __repr__(self) -> str:
        return f"{self.line}:{self.column}"


class Span(NamedTuple):
    start: Position
    end: Position
    file: Optional[str]

    @classmethod
    def from_node(
        cls, node: Node, src_file_hash: SourceFileHash, file: Optional[str]
    ) -> "Span":
        start = Position(line=node.start_mark.line, column=node.start_mark.column)
        end = Position(line=node.end_mark.line, column=node.end_mark.column)
        return Span(start=start, end=end, file=file)

    def __repr__(self) -> str:
        return f"{self.start}-{self.end}"


# Actually recursive but mypy is unhelpful
YamlValue = Union[str, int, List[Any], Dict[str, Any]]
LocatedYamlValue = Union[str, int, List["YamlTree"], Dict["YamlTree", "YamlTree"]]


class YamlTree:
    def __init__(self, value: LocatedYamlValue, span: Span):
        self.value = value
        self.span = span

    @classmethod
    def wrap(cls, value: YamlValue, span: Span) -> "YamlTree":
        """
        Wraps a value in a YamlTree and attaches the span everywhere.

        This exists so you can take generate a datastructure from user input, but track all the errors within that
        datastructure back to the user input

        """
        if isinstance(value, list):
            return YamlTree(value=[YamlTree.wrap(x, span) for x in value], span=span)
        elif isinstance(value, dict):
            return YamlTree(
                value={
                    YamlTree.wrap(k, span): YamlTree.wrap(v, span)
                    for k, v in value.items()
                },
                span=span,
            )
        elif isinstance(value, YamlTree):
            return value
        else:
            return YamlTree(value, span)

    # __eq__ and _hash__ delegate to value to support `value['a']` working properly.
    # otherwise, since the key is _actually_ a `Located` object you'd need to give the
    # span to pull it out of the dictionary.
    def __eq__(self, other: Any) -> bool:
        return self.value.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"{self.span}: ---> {self.value}"

    def unroll(self) -> YamlValue:
        """
        Recursively expand the `self.value`, converting back to a normal datastructure
        """
        if isinstance(self.value, list):
            return [x.unroll() for x in self.value]
        elif isinstance(self.value, dict):
            return {str(k.unroll()): v.unroll() for k, v in self.value.items()}
        elif isinstance(self.value, YamlTree):
            return self.value.unroll()
        else:
            return self.value


def parse_yaml(contents: str) -> Dict[str, Any]:
    yaml = YAML()
    return yaml.load(StringIO(contents))  # type: ignore


def parse_yaml_preserve_spans(contents: str, filename: Optional[str]) -> YamlTree:
    file_hash = src_to_hash(contents)
    SpanBuilder().add_source(file_hash, contents)

    class SpanPreservingRuamelConstructor(RoundTripConstructor):
        def construct_object(self, node: Node, deep: bool = False) -> YamlTree:
            r = super().construct_object(node, deep)
            return YamlTree(
                r, Span.from_node(node, src_file_hash=file_hash, file=filename)
            )

    yaml = YAML()
    yaml.Constructor = SpanPreservingRuamelConstructor
    data = yaml.load(StringIO(contents))
    if not isinstance(data, YamlTree):
        raise Exception("Something has gone horribly wrong in the YAML parser")
    return data
