"""Jaccard measures for comparing annotations done by different workers.

They measure inter-annotator agreement for one task variant.
"""

from typing import List

from snippet_annotation.annotation import WorkerAnnotation
from snippet_annotation.measures.annotation_similarity import (
    WorkerAnnotationSimilarity,
)
from snippet_annotation.utilities.annotation_utilities import (
    find_intervals_chosen_by_n_workers,
    get_sum_of_intervals_length,
    merge_annotations,
)


class Jaccard(WorkerAnnotationSimilarity):
    """Class for strict Jaccard inter-annotator agreement measure."""

    def get_text_annotation_similarity(
        self,
        annotations: List[WorkerAnnotation],
    ) -> float:
        """Computes strict Jaccard inter-annotator agreement.

        Counts the length of intervals chosen by all annotators and divides it
        by the length of intervals chosen by any annotator in a given group.

        Args:
            annotations: Annotations done by several different workers in a
               given group for a single input text.

        Returns:
            Strict Jaccard inter-annotator agreement.
        """
        intersection = find_intervals_chosen_by_n_workers(
            annotations, len(annotations)
        )
        union = merge_annotations(annotations)
        if len(union) == 0:
            return 1.0
        return get_sum_of_intervals_length(
            intersection
        ) / get_sum_of_intervals_length(union)


class JaccardLenient(Jaccard):
    """Class for lenient Jaccard inter-annotator agreement measure."""

    def __init__(self, k: int) -> None:
        """Lenient Jaccard annotation similarity measure.

        Args:
            k: Minimal number of annotators needed for an interval to be
               considered.
        """
        self.k = k

    def get_text_annotation_similarity(
        self, annotations: List[WorkerAnnotation]
    ) -> float:
        """Computes lenient Jaccard inter-annotator agreement.

        Counts the length of intervals chosen by at least k different annotators
        and divides it by the length of intervals chosen by any annotator in a
        given group.

        Args:
            annotations: Annotations done by several different workers in a
               given group for a single input text.

        Returns:
            Lenient Jaccard inter-annotator agreement.
        """
        intersection = find_intervals_chosen_by_n_workers(annotations, self.k)
        union = merge_annotations(annotations)
        if len(union) == 0:
            return 1.0
        return get_sum_of_intervals_length(
            intersection
        ) / get_sum_of_intervals_length(union)
