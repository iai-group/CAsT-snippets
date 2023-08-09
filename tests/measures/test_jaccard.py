"""Tests for Jaccard inter-annotator measures."""

from typing import List

import pytest

from snippet_annotation.annotation import Interval, TaskAnnotations, WorkerType
from snippet_annotation.measures.jaccard import Jaccard, JaccardLenient
from tests.helper_functions import create_annotations_from_intervals


@pytest.mark.parametrize(
    ("intervals", "strict_measure_value"),
    [
        (
            [
                [
                    Interval(0, 4),
                    Interval(10, 14),
                    Interval(20, 24),
                    Interval(30, 34),
                ],
                [Interval(0, 4), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
            ],
            0.25,
        ),
        (
            [
                [
                    Interval(0, 4),
                    Interval(10, 14),
                    Interval(20, 24),
                    Interval(30, 34),
                ],
                [Interval(0, 4), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
                [Interval(0, 4), Interval(10, 14)],
            ],
            0.25,
        ),
        (
            [
                [Interval(0, 4), Interval(10, 14), Interval(20, 24)],
                [Interval(10, 14), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
                [Interval(30, 34)],
            ],
            0.0,
        ),
    ],
)
def test_get_text_annotation_similarity_strict_variant(
    intervals: List[List[Interval]],
    strict_measure_value: float,
):
    """Test for computing strict Jaccard inter-annotator agreement.

    Args:
        intervals: Intervals chosen by several different workers in a given
           group for a single input text.
        strict_measure_value: Expected value of the strict variant of the
           measure.
    """
    expected_annotations = create_annotations_from_intervals(intervals)
    jaccard_strict = Jaccard()
    assert (
        jaccard_strict.get_text_annotation_similarity(expected_annotations)
        == strict_measure_value
    )


@pytest.mark.parametrize(
    ("intervals", "n", "lenient_measure_value"),
    [
        (
            [
                [
                    Interval(0, 4),
                    Interval(10, 14),
                    Interval(20, 24),
                    Interval(30, 34),
                ],
                [Interval(0, 4), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
            ],
            2,
            0.75,
        ),
        (
            [
                [
                    Interval(0, 4),
                    Interval(10, 14),
                    Interval(20, 24),
                    Interval(30, 34),
                ],
                [Interval(0, 4), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
                [Interval(0, 4), Interval(10, 14)],
            ],
            3,
            0.25,
        ),
        (
            [
                [Interval(0, 4), Interval(10, 14), Interval(20, 24)],
                [Interval(10, 14), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
                [Interval(30, 34)],
            ],
            3,
            0.0,
        ),
    ],
)
def test_get_text_annotation_similarity_lenient_variant(
    intervals: List[List[Interval]],
    n: int,
    lenient_measure_value: float,
):
    """Test for computing lenient Jaccard inter-annotator agreement.

    Args:
        intervals: Intervals chosen by several different workers in a given
           group for a single input text.
        n: Minimal number of annotators needed for an interval to be
           considered.
        lenient_measure_value: Expected value of the lenient variant of the
           measure.
    """
    expected_annotations = create_annotations_from_intervals(intervals)
    jaccard_lenient_n = JaccardLenient(n)
    assert (
        jaccard_lenient_n.get_text_annotation_similarity(expected_annotations)
        == lenient_measure_value
    )


def test_get_task_inter_annotator_agreement():
    """Test for computing Jaccard measures for an entire task."""
    # Values of Jaccard measures for input text 1:
    # Strict: 0.25, Lenient(3): 0.5
    input_text_1_intervals = [
        [Interval(0, 4), Interval(10, 14), Interval(20, 24), Interval(30, 34)],
        [Interval(0, 4), Interval(20, 24)],
        [Interval(0, 4), Interval(20, 24)],
        [Interval(0, 4), Interval(30, 34)],
    ]
    input_text_1_worker_annotations = create_annotations_from_intervals(
        input_text_1_intervals
    )

    # Values of Jaccard measures for input text 2:
    # Strict: 0.25, Lenient(3): 0.25
    input_text_2_intervals = [
        [Interval(0, 4), Interval(10, 14), Interval(20, 24), Interval(30, 34)],
        [Interval(0, 4), Interval(20, 24)],
        [Interval(0, 4), Interval(30, 34)],
        [Interval(0, 4), Interval(10, 14)],
    ]
    input_text_2_worker_annotations = create_annotations_from_intervals(
        input_text_2_intervals
    )

    task_annotations = TaskAnnotations(
        annotations={
            (
                "q_1",
                "p_1",
            ): input_text_1_worker_annotations,
            (
                "q_2",
                "p_2",
            ): input_text_2_worker_annotations,
        },
        worker_type=WorkerType.MTURK_REGULAR,
    )

    jaccard = Jaccard()
    assert (
        jaccard.get_task_inter_annotator_agreement(task_annotations)
        == (0.25 + 0.25) / 2
    )
    jaccard_n = JaccardLenient(k=3)
    assert (
        jaccard_n.get_task_inter_annotator_agreement(task_annotations)
        == (0.5 + 0.25) / 2
    )
