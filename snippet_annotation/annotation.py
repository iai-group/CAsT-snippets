"""Classes to represent snippet annotations.

Annotations can be on the sentence or paragraph level. Every text in a
crowdsourcing task is annotated be several different workers. Each task
can be done by a group of different workers.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

# The query_id and text_id used to index the dictionary of annotations done by
# different workers.
QueryPassage = Tuple[str, str]


class ConfidenceScore(Enum):
    """Class for confidence scores for annotations."""

    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class WorkerType(Enum):
    """Class for worker types working on crowdsourcing tasks."""

    MTURK_REGULAR = 1
    MTURK_MASTER = 2
    EXPERT = 3
    PROLIFIC = 4


class TaskVariant(Enum):
    """Class for crowdsourcing tasks variants."""

    SENTENCES = 1
    PARAGRAPH = 2


@dataclass
class Interval:
    """Class for the start and end position of a snippet in a text."""

    # The start character position is included in the snippet.
    start: int
    # The end character position is not included in the snippet.
    end: int


@dataclass
class InputText:
    """Class for input text (a paragraph or a sentence) for annotation task."""

    # Text of the query.
    query: str
    # Id of the query.
    query_id: str
    # Text of the sentence or paragraph relevant to the query.
    text: str
    # Id of the sentence or the paragraph.
    text_id: str


@dataclass
class WorkerAnnotation:
    """Class for annotation made for a text by one worker."""

    # List of selected intervals.
    intervals: List[Interval]
    # Text that is annotated.
    input_text: InputText
    # Id of the worker.
    worker_id: str


@dataclass
class TaskAnnotations:
    """Class for all annotations collected in a crowdsourcing task.

    A crowdsourcing task collects all input texts annotated by multiple
    workers.
    """

    # Dictionary of annotations done by different workers for each text in the
    # task indexed by (query_id, text_id) tuples.
    annotations: Dict[QueryPassage, List[WorkerAnnotation]]
    # Type of workers working on the task.
    worker_type: WorkerType
    # Indicates whether annotations are sentence-based.
    sentence_based: bool = False
