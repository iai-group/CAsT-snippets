"""Tests for methods for converting annotations between task variants."""

from typing import List, Tuple

import pytest

from snippet_annotation.annotation import InputText, Interval, WorkerAnnotation
from snippet_annotation.utilities.conversion import (
    AnnotationSource,
    convert_paragraph_annotation_to_sentence_based,
    convert_paragraph_task_annotation_to_sentence_based,
    convert_worker_annotation_to_intervals,
)


@pytest.mark.parametrize(
    ("worker_annotation", "sentence_based", "source", "intervals"),
    [
        (
            (
                '[{"relevant-text-spans-single-passage-annotation":{"entities":'
                '[{"endOffset":596,"label":"relevant-text-span","startOffset":'
                '551},{"endOffset":997,"label":"relevant-text-span",'
                '"startOffset":746}]}}]'
            ),
            False,
            AnnotationSource.MTURK,
            [Interval(551, 596), Interval(746, 997)],
        ),
        (
            (
                '[{"relevant-text-spans-sentence":{"entities":[{"endOffset":'
                '853,"label":"relevant-text-span","startOffset":746},{'
                '"endOffset":918,"label":"relevant-text-span","startOffset":'
                '863},{"endOffset":989,"label":"relevant-text-span",'
                '"startOffset":937},{"endOffset":1103,"label":"relevant-text-'
                'span","startOffset":999},{"endOffset":1248,"label":"relevant-'
                'text-span","startOffset":1105}]}}]'
            ),
            True,
            AnnotationSource.MTURK,
            [
                Interval(746, 853),
                Interval(863, 918),
                Interval(937, 989),
                Interval(999, 1103),
                Interval(1105, 1248),
            ],
        ),
        (
            (
                '[{"relevant-text-spans-prolific-annotation":{"entities":'
                '[{"endOffset":596,"label":"relevant-text-span","startOffset":'
                '551},{"endOffset":997,"label":"relevant-text-span",'
                '"startOffset":746}]}}]'
            ),
            False,
            AnnotationSource.PROLIFIC,
            [Interval(551, 596), Interval(746, 997)],
        ),
    ],
)
def test_convert_worker_annotation_to_intervals(
    worker_annotation: str,
    sentence_based: bool,
    source: AnnotationSource,
    intervals: List[Interval],
):
    """Test for converting worker annotation to a list of intervals.

    Args:
        worker_annotation: Worker annotation as raw text in MTurk format.
        sentence_based: Indicates whether the annotation is sentence-based.
        source: Source of the annotation.
        intervals: List of intervals expected to be returned by the method.
    """
    assert (
        convert_worker_annotation_to_intervals(
            worker_annotation, sentence_based, source
        )
        == intervals
    )


@pytest.mark.parametrize(
    (
        "paragraph_intervals",
        "sentences_intervals",
        "paragraph_input_text",
        "sentences_input_texts",
        "sentences",
    ),
    [
        (
            [Interval(0, 5), Interval(12, 17), Interval(24, 29)],
            [[Interval(0, 5)], [Interval(0, 5)], [Interval(0, 5)]],
            InputText(
                "Test query",
                "q_1",
                "Sentence 1. Sentence 2. Sentence 3.",
                "p_1",
            ),
            [
                InputText("Test query", "q_1", "Sentence 1.", "s_1"),
                InputText("Test query", "q_1", "Sentence 2.", "s_2"),
                InputText("Test query", "q_1", "Sentence 3.", "s_3"),
            ],
            [
                ("Sentence 1.", "s_1"),
                ("Sentence 2.", "s_2"),
                ("Sentence 3.", "s_3"),
            ],
        ),
        (
            [Interval(0, 29)],
            [[Interval(0, 10)], [Interval(0, 10)], [Interval(0, 5)]],
            InputText(
                "Test query",
                "q_1",
                "Sentence 1. Sentence 2. Sentence 3.",
                "p_1",
            ),
            [
                InputText("Test query", "q_1", "Sentence 1.", "s_1"),
                InputText("Test query", "q_1", "Sentence 2.", "s_2"),
                InputText("Test query", "q_1", "Sentence 3.", "s_3"),
            ],
            [
                ("Sentence 1.", "s_1"),
                ("Sentence 2.", "s_2"),
                ("Sentence 3.", "s_3"),
            ],
        ),
    ],
)
def test_convert_paragraph_annotation_to_sentence_based(
    paragraph_intervals: List[Interval],
    sentences_intervals: List[List[Interval]],
    paragraph_input_text: InputText,
    sentences_input_texts: List[InputText],
    sentences: List[Tuple[str, str]],
):
    """Test for converting paragraph-based annotation to sentence level.

    Intervals in paragraph-based annotations are contained within
    individual sentences.

    Args:
        paragraph_intervals: Paragraph-level annotations.
        sentences_intervals: Expected sentence-level annotations.
        paragraph_input_text: Paragraph-based sample input text.
        sentences_input_texts: Sentence-based sample input texts for 3
           sentences.
        sentences: List of (sentence, sentence_id) tuples corresponding to the
           sample paragraph.
    """
    paragraph_annotation = WorkerAnnotation(
        intervals=paragraph_intervals,
        input_text=paragraph_input_text,
        worker_id="w_1",
    )

    sentences_annotations = convert_paragraph_annotation_to_sentence_based(
        paragraph_annotation, sentences
    )
    assert all(
        [
            sentence_annotations.intervals == sentence_intervals
            for sentence_annotations, sentence_intervals in zip(
                sentences_annotations, sentences_intervals
            )
        ]
    )
    assert all(
        [
            sentence_annotations.input_text.text_id == input_text.text_id
            for sentence_annotations, input_text in zip(
                sentences_annotations, sentences_input_texts
            )
        ]
    )
    assert all(
        [
            sentence_annotations.input_text.query_id == input_text.query_id
            for sentence_annotations, input_text in zip(
                sentences_annotations, sentences_input_texts
            )
        ]
    )


def test_convert_paragraph_task_annotation_to_sentence_based():
    """Test for converting paragraph task annotations to sentence-level."""
    paragraph_annotations = {
        ("q_1", "p_1"): [
            WorkerAnnotation(
                input_text=InputText(
                    "Test query 1",
                    "q_1",
                    "Sentence 1. Sentence 2. Sentence 3.",
                    "p_1",
                ),
                intervals=[Interval(0, 5), Interval(12, 17), Interval(24, 29)],
                worker_id="w_1",
            ),
        ],
        ("q_2", "p_2"): [
            WorkerAnnotation(
                input_text=InputText(
                    "Test query 1",
                    "q_2",
                    "Sentence 4. Sentence 5. Sentence 6.",
                    "p_2",
                ),
                intervals=[Interval(0, 29)],
                worker_id="w_2",
            ),
        ],
    }
    expected_sentences_annotations = {
        ("q_1", "q_1--p_1--0"): [
            WorkerAnnotation(
                input_text=InputText(
                    "Test query 1",
                    "q_1",
                    "Sentence 1.",
                    "q_1--p_1--0",
                ),
                intervals=[Interval(0, 5)],
                worker_id="w_1",
            ),
        ],
        ("q_1", "q_1--p_1--1"): [
            WorkerAnnotation(
                input_text=InputText(
                    "Test query 1",
                    "q_1",
                    "Sentence 2.",
                    "q_1--p_1--1",
                ),
                intervals=[Interval(0, 5)],
                worker_id="w_1",
            ),
        ],
        ("q_1", "q_1--p_1--2"): [
            WorkerAnnotation(
                input_text=InputText(
                    "Test query 1",
                    "q_1",
                    "Sentence 3.",
                    "q_1--p_1--2",
                ),
                intervals=[Interval(0, 5)],
                worker_id="w_1",
            ),
        ],
        ("q_2", "q_2--p_2--0"): [
            WorkerAnnotation(
                input_text=InputText(
                    "Test query 1",
                    "q_2",
                    "Sentence 4.",
                    "q_2--p_2--0",
                ),
                intervals=[Interval(0, 10)],
                worker_id="w_2",
            ),
        ],
        ("q_2", "q_2--p_2--1"): [
            WorkerAnnotation(
                input_text=InputText(
                    "Test query 1",
                    "q_2",
                    "Sentence 5.",
                    "q_2--p_2--1",
                ),
                intervals=[Interval(0, 10)],
                worker_id="w_2",
            ),
        ],
        ("q_2", "q_2--p_2--2"): [
            WorkerAnnotation(
                input_text=InputText(
                    "Test query 1",
                    "q_2",
                    "Sentence 6.",
                    "q_2--p_2--2",
                ),
                intervals=[Interval(0, 5)],
                worker_id="w_2",
            ),
        ],
    }

    sentences_annotations = convert_paragraph_task_annotation_to_sentence_based(
        paragraph_annotations
    )

    assert sentences_annotations == expected_sentences_annotations
