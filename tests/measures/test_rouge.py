"""Tests for computing ROUGE-like measures."""

from typing import Dict, List

import pytest
from snippet_annotation.annotation import InputText, Interval, WorkerType
from snippet_annotation.measures.rouge import Rouge, RougeMeasure, RougeVariant
from tests.helper_functions import (
    create_annotations_from_intervals,
    create_task_annotations_from_intervals,
)


@pytest.mark.parametrize(
    ("reference_intervals", "worker_intervals", "measures_values"),
    [
        (
            [
                Interval(0, 4),
                Interval(10, 14),
                Interval(20, 24),
                Interval(30, 34),
            ],
            [Interval(0, 4), Interval(20, 24)],
            {
                RougeMeasure.PRECISION: 1,
                RougeMeasure.RECALL: 0.5,
                RougeMeasure.F1: 2 / 3,
            },
        ),
        (
            [Interval(0, 4), Interval(30, 34)],
            [Interval(0, 4), Interval(10, 14)],
            {
                RougeMeasure.PRECISION: 0.5,
                RougeMeasure.RECALL: 0.5,
                RougeMeasure.F1: 0.5,
            },
        ),
        (
            [Interval(10, 14), Interval(20, 24)],
            [Interval(30, 34)],
            {
                RougeMeasure.PRECISION: 0.0,
                RougeMeasure.RECALL: 0.0,
                RougeMeasure.F1: 0.0,
            },
        ),
    ],
)
def test_get_reference_annotator_agreement(
    reference_intervals: List[Interval],
    worker_intervals: List[Interval],
    measures_values: Dict[RougeMeasure, float],
):
    """Test for computing ROUGE-like similarity against reference annotation.

    Args:
        reference_intervals: Reference intervals.
        worker_intervals: Worker intervals chosen for the same input text.
        measures_values: Dictionary with expected value for each measure.
    """
    assert all(
        [
            Rouge(
                rouge_measure=measure, rouge_variant=RougeVariant.MEAN
            )._get_reference_annotator_agreement(
                reference_intervals, worker_intervals
            )
            == measure_value
            for measure, measure_value in measures_values.items()
        ]
    )


@pytest.mark.parametrize(
    ("intervals", "most_similar"),
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
                [Interval(0, 4), Interval(10, 14)],
            ],
            [
                Interval(0, 4),
                Interval(10, 14),
                Interval(20, 24),
                Interval(30, 34),
            ],
        ),
        (
            [
                [Interval(0, 4), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
                [Interval(0, 4), Interval(10, 14)],
            ],
            [Interval(0, 4), Interval(20, 24)],
        ),
    ],
)
def test_find_most_similar_annotation(
    intervals: List[List[Interval]],
    most_similar: List[Interval],
):
    """Test for finding the most similar annotation to others in a group.

    Args:
        intervals: List of intervals chosen for the same text by a group of
           workers.
        most_similar: Expected list of intervals from annotation most similar
           to others in a group.

    Returns:
        The list of intervals from annotation that is most similar to the others
        in a group.
    """
    annotations = create_annotations_from_intervals(intervals)
    rouge = Rouge(
        rouge_measure=RougeMeasure.PRECISION, rouge_variant=RougeVariant.MEAN
    )
    assert (
        rouge._find_most_similar_annotation(annotations).intervals
        == most_similar
    )


@pytest.mark.parametrize(
    ("reference_intervals", "worker_intervals", "measures_values"),
    [
        (
            # P:  [ 3/4,    1,      1/2,    1/4,    0,  1/2]    -> 3/6
            # R:  [ 1,      2/3,    1/3,    1,      0,  1]      -> 4/6
            # F1: [ 6/7,    4/5,    2/5,    2/5     0,  2/3]    -> 328/630
            [
                [Interval(0, 4), Interval(10, 14), Interval(20, 24)],
                [Interval(30, 34)],
            ],
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
            {
                RougeMeasure.PRECISION: 3 / 6,
                RougeMeasure.RECALL: 4 / 6,
                RougeMeasure.F1: 328 / 630,
            },
        ),
        (
            # P:  [ 2/3,    0,  1/2,    1/3,    1,      1/2]    -> 3/6
            # R:  [ 1,      0,  1/2,    1/2,    1/2,    1/2]    -> 3/6
            # F1: [ 4/5,    0,  1/2,    2/5,    2/3,    1/2]    -> 43/90
            [
                [Interval(0, 4), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
            ],
            [
                [Interval(0, 4), Interval(10, 14), Interval(20, 24)],
                [Interval(30, 34)],
                [Interval(0, 4), Interval(10, 14)],
            ],
            {
                RougeMeasure.PRECISION: 3 / 6,
                RougeMeasure.RECALL: 3 / 6,
                RougeMeasure.F1: 43 / 90,
            },
        ),
    ],
)
def test_get_text_reference_annotators_agreement_mean(
    reference_intervals: List[List[Interval]],
    worker_intervals: List[List[Interval]],
    measures_values: Dict[RougeMeasure, float],
):
    """Test for computing mean ROUGE measure against reference annotations.

    Args:
        reference_intervals: Reference intervals.
        worker_intervals: Workers intervals chosen for the same input text.
        measures_values: Dictionary with expected value for each measure.
    """
    reference_annotations = create_annotations_from_intervals(
        reference_intervals
    )
    worker_annotations = create_annotations_from_intervals(worker_intervals)

    assert all(
        [
            pytest.approx(
                Rouge(
                    rouge_measure=measure, rouge_variant=RougeVariant.MEAN
                ).get_text_reference_annotators_agreement(
                    reference_annotations, worker_annotations
                ),
                0.0001,
            )
            == measure_value
            for measure, measure_value in measures_values.items()
        ]
    )


@pytest.mark.parametrize(
    ("reference_intervals", "worker_intervals", "measures_values"),
    [
        (
            # P:  [ 2/3,    1/3]    -> 1/2
            # R:  [ 2/3,    1]      -> 5/6
            # F1: [ 2/3,    1/2]    -> 7/12
            [
                [Interval(0, 4), Interval(10, 14), Interval(20, 24)],
                [Interval(30, 34)],
            ],
            [
                [
                    Interval(0, 4),
                    Interval(10, 14),
                    Interval(20, 24),
                    Interval(30, 34),
                ],
                [Interval(0, 4), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
                # majority intervals (n=2): [(0, 4), (20, 24), (30, 34)]
            ],
            {
                RougeMeasure.PRECISION: 1 / 2,
                RougeMeasure.RECALL: 5 / 6,
                RougeMeasure.F1: 7 / 12,
            },
        )
    ],
)
def test_get_text_reference_annotators_agreement_majority(
    reference_intervals: List[List[Interval]],
    worker_intervals: List[List[Interval]],
    measures_values: Dict[RougeMeasure, float],
):
    """Test for computing majority ROUGE measure against reference annotations.

    Args:
        reference_intervals: Reference intervals.
        worker_intervals: Workers intervals chosen for the same input text.
        measures_values: Dictionary with expected value for each measure.
    """
    reference_annotations = create_annotations_from_intervals(
        reference_intervals
    )
    worker_annotations = create_annotations_from_intervals(worker_intervals)

    assert all(
        [
            pytest.approx(
                Rouge(
                    rouge_measure=measure,
                    rouge_variant=RougeVariant.MAJORITY,
                    n=2,
                ).get_text_reference_annotators_agreement(
                    reference_annotations, worker_annotations
                ),
                0.0001,
            )
            == measure_value
            for measure, measure_value in measures_values.items()
        ]
    )


@pytest.mark.parametrize(
    ("reference_intervals", "worker_intervals", "measures_values"),
    [
        (
            # P:  [ 3/4,    1/4]    -> 1/2
            # R:  [ 1,      1]      -> 1
            # F1: [ 6/7,    2/5]    -> 44/70
            [
                [Interval(0, 4), Interval(10, 14), Interval(20, 24)],
                [Interval(30, 34)],
            ],
            [
                [
                    Interval(0, 4),
                    Interval(10, 14),
                    Interval(20, 24),
                    Interval(30, 34),
                ],
                [Interval(0, 4), Interval(20, 24)],
                [Interval(0, 4), Interval(30, 34)],
                # similarity intervals: [(0, 4), (10, 14), (20, 24), (30, 34)]
            ],
            {
                RougeMeasure.PRECISION: 1 / 2,
                RougeMeasure.RECALL: 1.0,
                RougeMeasure.F1: 44 / 70,
            },
        ),
        (
            [
                [Interval(0, 4), Interval(10, 14), Interval(20, 24)],
                [Interval(30, 34)],
            ],
            [
                [Interval(0, 4), Interval(30, 34)],
                # similarity intervals: None
            ],
            {
                RougeMeasure.PRECISION: 0,
                RougeMeasure.RECALL: 0,
                RougeMeasure.F1: 0,
            },
        ),
    ],
)
def test_get_text_reference_annotators_agreement_similarity(
    reference_intervals: List[List[Interval]],
    worker_intervals: List[List[Interval]],
    measures_values: Dict[RougeMeasure, float],
):
    """Test for computing similarity ROUGE against reference annotations.

    Args:
        reference_intervals: Reference intervals.
        worker_intervals: Workers intervals chosen for the same input text.
        measures_values: Dictionary with expected value for each measure.
    """
    reference_annotations = create_annotations_from_intervals(
        reference_intervals
    )
    worker_annotations = create_annotations_from_intervals(worker_intervals)
    assert all(
        [
            pytest.approx(
                Rouge(
                    rouge_measure=measure, rouge_variant=RougeVariant.SIMILARITY
                ).get_text_reference_annotators_agreement(
                    reference_annotations, worker_annotations
                ),
                0.0001,
            )
            == measure_value
            for measure, measure_value in measures_values.items()
        ]
    )


def test_get_task_expert_annotator_agreement():
    """Test for computing ROUGE-like measures for an entire task."""
    input_texts = [
        InputText("Query 1", "q_1", "Text 1.", "t_1"),
        InputText("Query 2", "q_2", "Text 2.", "t_2"),
    ]
    # P:    [3/4,  1,      1/2,    1/2,    1,  1/2,    1/2,    1/2,    1/2]
    # R:    [1,    2/3,    1/3,    1,      1,  1/2,    1,      1/2,    1/2]
    # F1:   [6/7,  4/5,    2/5,    2/3,    1,  1/2,    2/3,    1/2,    1/2]
    # Mean measure values -> P: 23/36, R: 13/18, F1: 1237/1890
    expert_intervals_1 = [
        [Interval(0, 4), Interval(10, 14), Interval(20, 24)],
        [Interval(0, 4), Interval(20, 24)],
        [Interval(0, 4), Interval(10, 14)],
    ]
    # Majority interval (n=2): [(0, 4), (20, 24), (30, 34)]
    # P:    [2/3,   2/3,    1/3] -> 5/9
    # R:    [2/3,   1,      1/2] -> 13/18
    # F1:   [2/3,   4/5,    2/5] -> 28/45
    worker_intervals_1 = [
        [
            Interval(0, 4),
            Interval(10, 14),
            Interval(20, 24),
            Interval(30, 34),
        ],  # Sum of F1 to others: 8/6 <- most similar
        [Interval(0, 4), Interval(20, 24)],  # Sum of F1 to others: 7/6
        [Interval(0, 4), Interval(30, 34)],  # Sum of F1 to others: 7/6
    ]
    # Most similar: [(0, 4), (10, 14), (20, 24), (30, 34)]
    # P:    [3/4,   1/2,    1/2] -> 7/12
    # R:    [1,     1,      1]   -> 1
    # F1:   [6/7,   2/3,    2/3] -> 46/63

    # P:    [1,     1,      1,      1/2,    1/2,    0,  1/2,    1/2,    0]
    # R:    [1/2,   1/2,    1/4,    1/2,    1/2,    0,  1/2,    1/2,    0]
    # F1:   [2/3,   2/3,    2/5,    1/2,    1/2,    0,  1/2,    1/2,    0]
    # Mean measure values -> P: 5/9, R: 13/36, F1: 56/135
    expert_intervals_2 = [
        [Interval(0, 4), Interval(10, 14), Interval(20, 24), Interval(30, 34)],
        [Interval(0, 4), Interval(20, 24)],
        [Interval(0, 4), Interval(20, 24)],
    ]
    # Majority interval (n=2): [(10, 14)]
    # P:    [1,     0,      0] -> 1/3
    # R:    [1/4,   0,      0] -> 1/12
    # F1:   [2/5,   0,      0] -> 2/15
    worker_intervals_2 = [
        [
            Interval(0, 4),
            Interval(10, 14),
        ],  # Sum of F1 to others: 1/2 <- most similar
        [Interval(10, 14), Interval(20, 24)],  # Sum of F1 to others: 1/2
        [Interval(30, 34)],  # Sum of F1 to others: 0
    ]
    # Most similar: [(0, 4), (10, 14)]
    # P:    [1,     1/2,    1/2] -> 2/3
    # R:    [1/2,   1/2,    1/2] -> 1/2
    # F1:   [2/3,   1/2,    1/2] -> 5/9

    worker_task_annotations = create_task_annotations_from_intervals(
        input_texts,
        [worker_intervals_1, worker_intervals_2],
        WorkerType.MTURK_REGULAR,
    )
    expert_task_annotations = create_task_annotations_from_intervals(
        input_texts, [expert_intervals_1, expert_intervals_2], WorkerType.EXPERT
    )

    rouge_expected_values = {
        RougeVariant.MEAN: {
            RougeMeasure.PRECISION: (23 / 36 + 5 / 9) / 2,
            RougeMeasure.RECALL: (13 / 18 + 13 / 36) / 2,
            RougeMeasure.F1: (1237 / 1890 + 56 / 135) / 2,
        },
        RougeVariant.MAJORITY: {
            RougeMeasure.PRECISION: (5 / 9 + 1 / 3) / 2,
            RougeMeasure.RECALL: (13 / 18 + 1 / 12) / 2,
            RougeMeasure.F1: (28 / 45 + 2 / 15) / 2,
        },
        RougeVariant.SIMILARITY: {
            RougeMeasure.PRECISION: (7 / 12 + 2 / 3) / 2,
            RougeMeasure.RECALL: (1 + 1 / 2) / 2,
            RougeMeasure.F1: (46 / 63 + 5 / 9) / 2,
        },
    }
    assert all(
        [
            pytest.approx(
                Rouge(
                    rouge_measure=measure, rouge_variant=variant, n=2
                ).get_task_reference_annotator_agreement(
                    expert_task_annotations, worker_task_annotations
                ),
                0.00001,
            )
            == measure_value
            for variant, measures_values in rouge_expected_values.items()
            for measure, measure_value in measures_values.items()
        ]
    )
