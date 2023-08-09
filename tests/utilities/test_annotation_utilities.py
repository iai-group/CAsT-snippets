"""Test for utility functions for working with annotations."""

from typing import List

import pytest

from snippet_annotation.annotation import Interval
from snippet_annotation.utilities.annotation_utilities import (
    find_intervals_chosen_by_n_workers,
    get_intervals_intersection,
    get_sum_of_intervals_length,
    merge_annotations,
)
from tests.helper_functions import create_annotations_from_intervals


@pytest.mark.parametrize(
    ("annotation_a", "annotation_b", "intersection"),
    [
        (
            [Interval(551, 596), Interval(746, 997)],
            [
                Interval(746, 853),
                Interval(863, 918),
                Interval(937, 989),
                Interval(999, 1103),
                Interval(1105, 1248),
            ],
            [Interval(746, 853), Interval(863, 918), Interval(937, 989)],
        ),
        (
            [Interval(551, 745)],
            [
                Interval(746, 853),
                Interval(863, 918),
                Interval(937, 989),
                Interval(999, 1103),
                Interval(1105, 1248),
            ],
            [],
        ),
    ],
)
def test_get_annotations_intersection(
    annotation_a: List[Interval],
    annotation_b: List[Interval],
    intersection: List[Interval],
):
    """Test for finding the intersection of intervals.

    Args:
        annotation_a: The first list of intervals.
        annotation_b: The second list of intervals.
        intersection:  List of intervals that are the intersection.
    """
    assert (
        get_intervals_intersection(annotation_a, annotation_b) == intersection
    )


@pytest.mark.parametrize(
    ("intervals", "length"),
    [
        ([Interval(551, 596), Interval(746, 997)], 296),
        (
            [
                Interval(746, 853),
                Interval(863, 918),
                Interval(937, 989),
                Interval(999, 1103),
                Interval(1105, 1248),
            ],
            461,
        ),
        ([], 0),
    ],
)
def test_get_sum_of_intervals_length(intervals: List[Interval], length: int):
    """Test for counting the sum of the length of intervals.

    Args:
        intervals: List of intervals.
        length: The overall length of intervals.
    """
    assert get_sum_of_intervals_length(intervals) == length


@pytest.mark.parametrize(
    ("intervals", "merged_intervals"),
    [
        (
            [
                [
                    Interval(746, 853),
                    Interval(863, 918),
                    Interval(937, 989),
                    Interval(999, 1103),
                    Interval(1105, 1248),
                ],
                [Interval(721, 998), Interval(1000, 1103)],
                [Interval(721, 998)],
                [
                    Interval(544, 596),
                    Interval(762, 853),
                    Interval(864, 918),
                    Interval(929, 997),
                ],
                [
                    Interval(746, 792),
                    Interval(868, 919),
                    Interval(1063, 1090),
                    Interval(1229, 1247),
                ],
            ],
            [
                Interval(544, 596),
                Interval(721, 998),
                Interval(999, 1103),
                Interval(1105, 1248),
            ],
        ),
        (
            [[Interval(1, 3)], [Interval(3, 5), Interval(5, 6)]],
            [Interval(1, 6)],
        ),
        (
            [[Interval(1, 2)], [Interval(1, 3)], [Interval(1, 4)]],
            [Interval(1, 4)],
        ),
        (
            [[Interval(1, 2)], [Interval(3, 4)], [Interval(5, 6)]],
            [Interval(1, 2), Interval(3, 4), Interval(5, 6)],
        ),
    ],
)
def test_merge_annotations(
    intervals: List[List[Interval]],
    merged_intervals: List[Interval],
):
    """Test for merging lists of possibly intersecting intervals.

    Args:
        intervals: Lists of intervals chosen by different workers.
        merged_intervals: Union of lists of intervals.
    """
    annotations = create_annotations_from_intervals(intervals)
    assert merge_annotations(annotations) == merged_intervals


@pytest.mark.parametrize(
    ("intervals", "n", "majority_intervals"),
    [
        (
            [
                [
                    Interval(746, 853),
                    Interval(863, 918),
                    Interval(937, 989),
                    Interval(999, 1103),
                    Interval(1105, 1248),
                ],
                [Interval(721, 998), Interval(1000, 1103)],
                [Interval(721, 998)],
                [
                    Interval(544, 596),
                    Interval(762, 853),
                    Interval(864, 918),
                    Interval(929, 997),
                ],
                [
                    Interval(746, 792),
                    Interval(868, 919),
                    Interval(1063, 1090),
                    Interval(1229, 1247),
                ],
            ],
            3,
            [
                Interval(746, 853),
                Interval(863, 919),
                Interval(929, 997),
                Interval(1063, 1090),
            ],
        ),
        ([[Interval(1, 2)], [Interval(3, 4)], [Interval(5, 6)]], 5, []),
        (
            [
                [Interval(1, 2)],
                [Interval(1, 3)],
                [Interval(1, 4)],
                [Interval(5, 7)],
                [Interval(5, 9)],
            ],
            2,
            [Interval(1, 3), Interval(5, 7)],
        ),
        (
            [
                [Interval(1, 6)],
                [Interval(2, 6)],
                [Interval(4, 6)],
            ],
            2,
            [Interval(2, 6)],
        ),
    ],
)
def test_find_intervals_chosen_by_n_workers(
    intervals: List[List[Interval]],
    n: int,
    majority_intervals: List[Interval],
):
    """Test for finding intervals annotated by at least n workers in a group.

    Args:
        intervals: List of intervals chosen by different workers.
        n: The minimum amount of workers in the group that need to annotate an
           interval.
        majority_intervals: List of intervals chosen by at least n different
           workers in a group.
    """
    annotations = create_annotations_from_intervals(intervals)
    assert (
        find_intervals_chosen_by_n_workers(annotations, n) == majority_intervals
    )
