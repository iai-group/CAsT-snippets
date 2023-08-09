"""Tests for loading annotated data from files."""

from typing import List

import pytest

from snippet_annotation.annotation import InputText, Interval, WorkerAnnotation
from snippet_annotation.utilities.conversion import AnnotationSource
from snippet_annotation.utilities.data_loader import (
    load_worker_annotations_from_file,
)


@pytest.mark.parametrize(
    (
        "task_data_path",
        "source",
        "input_text",
        "workers_intervals",
        "workers_ids",
    ),
    [
        (
            "tests/data/test_paragraph_annotations.csv",
            AnnotationSource.MTURK,
            InputText(
                query=(
                    "I remember Glasgow hosting COP26 last year, but "
                    "unfortunately I was out of the loop. What was the "
                    "conference about?"
                ),
                query_id="132_1-1",
                text=(
                    "2021 United Nations Climate Change Conference - Wikipedia "
                    "2021 United Nations ..."
                ),
                text_id="MARCO_16_3117875026-1",
            ),
            [
                [Interval(551, 596), Interval(746, 997)],
                [Interval(1000, 1103), Interval(1105, 1248)],
            ],
            ["A2FYHFWUJ7IS36", "A2FYHFWUJ7IS37"],
        ),
        (
            "tests/data/test_sentence_annotations.csv",
            AnnotationSource.MTURK,
            InputText(
                query=(
                    "I remember Glasgow hosting COP26 last year, but "
                    "unfortunately I was out of the loop. What was the "
                    "conference about?"
                ),
                query_id="132_1-1",
                text=(
                    "The conference is set to incorporate the 26th Conference "
                    "of the Parties to the United Nations ..."
                ),
                text_id="132_1-1--MARCO_16_3117875026-1--2",
            ),
            [[Interval(0, 277)], [Interval(25, 71)]],
            ["A1GOLJMO4GID3I", "A26ZENZ5G8AEGM"],
        ),
        (
            "tests/data/test_prolific_annotations.csv",
            AnnotationSource.PROLIFIC,
            InputText(
                query=(
                    "I remember Glasgow hosting COP26 last year, but "
                    "unfortunately I was out of the loop. What was the "
                    "conference about?"
                ),
                query_id="132_1-1",
                text=(
                    "2021 United Nations Climate Change Conference - Wikipedia "
                    "2021 United Nations ..."
                ),
                text_id="MARCO_16_3117875026-1",
            ),
            [
                [Interval(20, 34), Interval(1019, 1102), Interval(1225, 1248)],
                [Interval(5, 45), Interval(545, 596), Interval(721, 918)],
            ],
            ["5f2424359c5da10009d035be", "5d2b45b9f7ef930001c5fa2d"],
        ),
    ],
)
def test_load_worker_annotations_from_file(
    task_data_path: str,
    source: AnnotationSource,
    input_text: InputText,
    workers_intervals: List[List[Interval]],
    workers_ids: List[str],
):
    """Test for loading annotations for a given task from file.

    Args:
        task_data_path: Path to the file with annotations.
        source: Source of the annotation.
        input_text: Sample input text.
        workers_intervals: Annotated intervals.
        workers_ids: Ids of workers working on annotations.
    """
    workers_annotations = [
        WorkerAnnotation(
            intervals=worker_intervals,
            input_text=input_text,
            worker_id=worker_id,
        )
        for worker_intervals, worker_id in zip(workers_intervals, workers_ids)
    ]
    annotations = load_worker_annotations_from_file(task_data_path, source)
    expected_annotations = {
        (input_text.query_id, input_text.text_id): workers_annotations,
    }

    assert len(annotations) == len(expected_annotations)
    assert all(
        [
            annotation == expected_annotation
            for annotation, expected_annotation in zip(
                annotations, expected_annotations
            )
        ]
    )
