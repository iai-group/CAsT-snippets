"""Utility functions for working with annotations."""

import itertools
from collections import defaultdict
from typing import Dict, List

from snippet_annotation.annotation import Interval, WorkerAnnotation


def get_intervals_intersection(
    intervals_a: List[Interval], intervals_b: List[Interval]
) -> List[Interval]:
    """Finds the intersection of intervals in two different annotations.

    Args:
        intervals_a: The first list of intervals.
        intervals_b: The second list of intervals.

    Returns:
        List of intervals that are the intersection.
    """
    intersection = []
    interval_a_id = interval_b_id = 0

    while interval_a_id < len(intervals_a) and interval_b_id < len(intervals_b):
        lower_bound = max(
            intervals_a[interval_a_id].start, intervals_b[interval_b_id].start
        )
        upper_bound = min(
            intervals_a[interval_a_id].end, intervals_b[interval_b_id].end
        )
        if lower_bound <= upper_bound:
            intersection.append(Interval(lower_bound, upper_bound))

        if intervals_a[interval_a_id].end < intervals_b[interval_b_id].end:
            interval_a_id += 1
        else:
            interval_b_id += 1

    return intersection


def get_sum_of_intervals_length(intervals: List[Interval]) -> int:
    """Counts the sum of the length of intervals (in terms of characters).

    Args:
        intervals: List of intervals.

    Returns:
        The overall length of intervals.
    """
    return sum([interval.end - interval.start for interval in intervals])


def merge_annotations(annotations: List[WorkerAnnotation]) -> List[Interval]:
    """Creates union of intervals chosen by multiple annotators.

    For example having the following intervals chosen by three different workers
    (where interval (1,3) means that characters on positions 1 and 2 are
    chosen):
    Intervals in annotation 1: [(1, 3)]
    Intervals in annotation 2: [(3, 5), (6, 8)]
    Intervals in annotation 3: [(2, 3)]

    The merged intervals are the union of them:
    [(1, 5), (6, 8)]

    Args:
        annotations: List of annotations made by different workers.

    Returns:
        Union of lists of intervals.
    """
    intervals: List[Interval] = list(
        itertools.chain.from_iterable(
            [annotation.intervals for annotation in annotations]
        )
    )
    intervals = sorted(intervals, key=lambda interval: interval.start)
    if len(intervals) == 0:
        return []
    intervals_union = [intervals[0]]
    for interval in intervals[1:]:
        if (
            intervals_union[-1].start
            <= interval.start
            <= intervals_union[-1].end
        ):
            last_interval = intervals_union[-1]
            intervals_union.remove(last_interval)
            intervals_union.append(
                Interval(
                    last_interval.start, max(last_interval.end, interval.end)
                )
            )
        else:
            intervals_union.append(interval)
    return intervals_union


def find_intervals_chosen_by_n_workers(
    annotations: List[WorkerAnnotation], n: int
) -> List[Interval]:
    """Finds the intervals annotated by at least n workers in a group.

    Args:
        annotations: List of annotations made by a group of workers.
        n: The minimum amount of workers in the group that need to annotate an
           interval.

    Returns:
        List of intervals chosen by at least n workers in a group.
    """
    intervals_chosen_by_n = []
    intervals: List[Interval] = list(
        itertools.chain.from_iterable(
            [annotation.intervals for annotation in annotations]
        )
    )
    num_workers_per_position: Dict[int, int] = defaultdict(int)
    for interval in intervals:
        for position in range(interval.start, interval.end + 1):
            num_workers_per_position[position] += 1

    current_position = 0
    current_interval_start = -1
    while current_position < len(num_workers_per_position):
        if (
            num_workers_per_position[current_position] < n
            and current_interval_start != -1
        ):
            intervals_chosen_by_n.append(
                Interval(
                    current_interval_start,
                    current_position - 1,
                )
            )
            current_interval_start = -1
        elif (
            num_workers_per_position[current_position] >= n
            and current_interval_start == -1
        ):
            current_interval_start = current_position

        current_position += 1

    # Closing the interval that ends at the end of the text.
    if current_interval_start != -1:
        intervals_chosen_by_n.append(
            Interval(current_interval_start, current_position - 1)
        )

    return intervals_chosen_by_n
