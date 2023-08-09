"""Methods for converting annotations between task variants."""

import ast
from collections import defaultdict
from enum import Enum
from typing import Dict, List, Tuple

import nltk

from snippet_annotation.annotation import (
    InputText,
    Interval,
    QueryPassage,
    WorkerAnnotation,
)
from snippet_annotation.utilities.annotation_utilities import (
    get_intervals_intersection,
)

nltk.download("punkt")

MTURK_SENTENCE_ANNOTATION_NAME = "relevant-text-spans-sentence"
MTURK_PARAGRAPH_ANNOTATION_NAME = (
    "relevant-text-spans-single-passage-annotation"
)
PROLIFIC_PARAGRAPH_ANNOTATION_NAME = "relevant-text-spans-prolific-annotation"


class AnnotationSource(Enum):
    """Class for the source platform of the annotation."""

    MTURK = 1
    PROLIFIC = 2


def convert_worker_annotation_to_intervals(
    worker_annotation: str,
    sentence_based: bool = False,
    source: AnnotationSource = AnnotationSource.MTURK,
) -> List[Interval]:
    """Converts worker annotation to a list of intervals.

    Args:
        worker_annotation: Worker annotation as raw text in MTurk format.
        sentence_based (optional): Indicates whether the annotation is
           sentence-based. (Defaults to False.)
        source (optional): Source of the annotation. (Defaults to MTURK.)

    Returns:
        List of intervals.
    """
    annotation_name = (
        PROLIFIC_PARAGRAPH_ANNOTATION_NAME
        if source == AnnotationSource.PROLIFIC
        else MTURK_SENTENCE_ANNOTATION_NAME
        if sentence_based
        else MTURK_PARAGRAPH_ANNOTATION_NAME
    )
    intervals = ast.literal_eval(worker_annotation)[0][annotation_name][
        "entities"
    ]
    return list(
        map(
            lambda interval: Interval(
                int(interval["startOffset"]),
                int(interval["endOffset"]),
            ),
            intervals,
        )
    )


def convert_paragraph_annotation_to_sentence_based(
    annotation: WorkerAnnotation, sentences: List[Tuple[str, str]]
) -> List[WorkerAnnotation]:
    """Converts paragraph-based annotation to sentence level.

    Paragraph-based expert annotations need to be converted to sentence
    level for evaluation of sentence-based annotations.

    Args:
        annotation: Paragraph-based annotation.
        sentences: List of (sentence, sentence_id) tuples corresponding to the
           paragraph that is annotated.

    Returns:
        List of sentence-based annotations extracted from paragraph-based
        annotation.
    """
    sentence_annotations = []
    for sentence in sentences:
        start = annotation.input_text.text.index(sentence[0])
        end = start + len(sentence[0]) - 1
        intersecting_intervals = get_intervals_intersection(
            annotation.intervals, [Interval(start, end)]
        )
        sentence_intervals = [
            Interval(i.start - start, i.end - start)
            for i in intersecting_intervals
        ]
        sentence_input_text = InputText(
            query=annotation.input_text.query,
            query_id=annotation.input_text.query_id,
            text=sentence[0],
            text_id=sentence[1],
        )
        sentence_annotations.append(
            WorkerAnnotation(
                intervals=sentence_intervals,
                input_text=sentence_input_text,
                worker_id=annotation.worker_id,
            )
        )

    return sentence_annotations


def convert_paragraph_task_annotation_to_sentence_based(
    paragraph_task_annotations: Dict[QueryPassage, List[WorkerAnnotation]]
) -> Dict[QueryPassage, List[WorkerAnnotation]]:
    """Converts paragraph-level task annotations to sentence-level.

    Args:
        paragraph_task_annotations: Paragraph-based annotations for entire task.

    Returns:
        Sentence-based annotations extracted from paragraph-based annotation
        for entire task.
    """
    sentence_annotations = defaultdict(list)
    for paragraph_annotations in paragraph_task_annotations.values():
        for paragraph_annotation in paragraph_annotations:
            paragraph_sentences = nltk.sent_tokenize(
                paragraph_annotation.input_text.text
            )
            sentences = [
                (
                    paragraph_sentence,
                    "{}--{}--{}".format(
                        paragraph_annotation.input_text.query_id,
                        paragraph_annotation.input_text.text_id,
                        id,
                    ),
                )
                for id, paragraph_sentence in enumerate(paragraph_sentences)
            ]
            sentence_worker_annotations = (
                convert_paragraph_annotation_to_sentence_based(
                    paragraph_annotation, sentences
                )
            )
            for sentence_worker_annotation in sentence_worker_annotations:
                sentence_annotations[
                    (
                        sentence_worker_annotation.input_text.query_id,
                        sentence_worker_annotation.input_text.text_id,
                    )
                ].append(sentence_worker_annotation)

    return sentence_annotations
