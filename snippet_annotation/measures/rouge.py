"""ROUGE measures for comparing annotations made for different tasks.

Task variants include different type of annotator, different platform,
different level of annotations.
"""

from enum import Enum
from typing import List

from snippet_annotation.annotation import Interval, WorkerAnnotation
from snippet_annotation.measures.annotation_measure import AnnotationMeasure
from snippet_annotation.utilities.annotation_utilities import (
    find_intervals_chosen_by_n_workers,
    get_intervals_intersection,
    get_sum_of_intervals_length,
)


class RougeVariant(Enum):
    """Class for ROUGE measure variants."""

    # The final ROUGE measure is the mean of measures computed between every
    # pair of worker and reference annotation.
    MEAN = 1
    # The final ROUGE measure is the mean of measures computed between majority
    # intervals and every reference annotation.
    MAJORITY = 2
    # The final ROUGE measure is the mean of measures computed between the
    # worker annotations that are most similar to other workers' annotations in
    # terms of F1 measure and every reference annotation.
    SIMILARITY = 3


class RougeMeasure(Enum):
    """Class for different ROUGE measures."""

    PRECISION = 1
    RECALL = 2
    F1 = 3


class Rouge(AnnotationMeasure):
    """Class for ROUGE measures."""

    def __init__(
        self,
        rouge_measure: RougeMeasure,
        rouge_variant: RougeVariant,
        n: int = None,
    ) -> None:
        """ROUGE annotation similarity measure.

        Args:
            rouge_measure: ROUGE measure (precision, recall, or F1).
            rouge_variant: Variant of ROUGE measure.
            n: The minimum amount of workers in the group that need to annotate
               an interval for majority ROUGE measure variant.
        """
        self.rouge_measure = rouge_measure
        self.rouge_variant = rouge_variant
        self.n = n

    def get_text_reference_annotators_agreement(
        self,
        reference_annotations: List[WorkerAnnotation],
        worker_annotations: List[WorkerAnnotation],
    ) -> float:
        """Computes ROUGE similarity against reference annotations.

        The measure value is an average of agreements between reference and
        workers annotations for the same input text.

        Args:
            reference_annotations: Reference annotations.
            worker_annotations: Workers' annotations made for the same input
               text.

        Returns:
            Similarity of workers' annotations against reference annotations for
            the same input text.
        """
        worker_intervals_to_compare = []
        if self.rouge_variant == RougeVariant.MEAN:
            worker_intervals_to_compare = [
                worker_annotation.intervals
                for worker_annotation in worker_annotations
            ]
        elif self.rouge_variant == RougeVariant.MAJORITY:
            worker_intervals_to_compare = [
                find_intervals_chosen_by_n_workers(worker_annotations, self.n)
            ]
        elif self.rouge_variant == RougeVariant.SIMILARITY:
            most_similar_annotation = self._find_most_similar_annotation(
                worker_annotations
            )
            if most_similar_annotation is None:
                return 0
            worker_intervals_to_compare = [most_similar_annotation.intervals]

        measure_values = []
        for reference_annotation in reference_annotations:
            for worker_intervals in worker_intervals_to_compare:
                measure_values.append(
                    self._get_reference_annotator_agreement(
                        reference_annotation.intervals, worker_intervals
                    )
                )
        return sum(measure_values) / len(measure_values)

    def _get_reference_annotator_agreement(
        self,
        reference_intervals: List[Interval],
        worker_intervals: List[Interval],
    ) -> float:
        """Computes ROUGE similarity against reference annotation.

        Args:
            reference_annotation: Reference annotation.
            worker_annotation: Worker's annotation made for the same input text.

        Returns:
            ROUGE similarity of worker's annotation against reference
            annotation for the same input text.
        """
        intersection = get_intervals_intersection(
            reference_intervals, worker_intervals
        )
        nominator = get_sum_of_intervals_length(intersection)
        if nominator == 0:
            return 0.0
        precision = nominator / get_sum_of_intervals_length(worker_intervals)
        if self.rouge_measure == RougeMeasure.PRECISION:
            return precision
        recall = nominator / get_sum_of_intervals_length(reference_intervals)
        if self.rouge_measure == RougeMeasure.RECALL:
            return recall
        f1 = 2 * (precision * recall) / (precision + recall)
        if self.rouge_measure == RougeMeasure.F1:
            return f1
        return None

    def _find_most_similar_annotation(
        self,
        annotations: List[WorkerAnnotation],
    ) -> WorkerAnnotation:
        """Finds the annotation that is most similar to others in a group.

        Annotations are compared in terms of F1 measure.

        Args:
            annotations: List of annotations done for the same text by a group
               of workers.

        Returns:
            The annotation that is most similar to the others in a group.
        """
        most_similar_f1 = -1.0
        most_similar_annotation = None
        rouge_f1 = Rouge(
            rouge_measure=RougeMeasure.F1, rouge_variant=RougeVariant.MEAN
        )
        for worker_annotation in annotations:
            remaining_annotations = [
                annotation
                for annotation in annotations
                if annotation is not worker_annotation
            ]
            if len(remaining_annotations) == 0:
                return None
            current_f1 = sum(
                [
                    rouge_f1.get_text_reference_annotators_agreement(
                        [worker_annotation], [remaining_annotation]
                    )
                    for remaining_annotation in remaining_annotations
                ]
            ) / len(remaining_annotations)
            if current_f1 > most_similar_f1:
                most_similar_f1 = current_f1
                most_similar_annotation = worker_annotation

        return most_similar_annotation
