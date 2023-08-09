"""Abstract class for similarity against reference annotations measures."""

from abc import ABC, abstractmethod
from typing import List

from snippet_annotation.annotation import TaskAnnotations, WorkerAnnotation


class AnnotationMeasure(ABC):
    """Abstract class for similarity against reference annotations measures."""

    @abstractmethod
    def get_text_reference_annotators_agreement(
        self,
        reference_annotations: List[WorkerAnnotation],
        worker_annotations: List[WorkerAnnotation],
    ) -> float:
        """Computes the similarity against reference annotations.

        The measure value is an average of agreements between each reference
        and workers' annotations for the same input text.

        Args:
            reference_annotations: Reference annotations.
            worker_annotations: Workers' annotations made for the same input
               text.

        Returns:
            Similarity of workers' annotations against reference annotations for
            the same input text.
        """
        raise NotImplementedError

    def get_task_reference_annotator_agreement(
        self,
        reference_task_annotations: TaskAnnotations,
        worker_task_annotations: TaskAnnotations,
    ) -> float:
        """Computes reference annotators and workers agreement on task-level.

        Args:
            reference_task_annotations: Reference annotations made for all texts
               in a task.
            worker_task_annotations: Annotations made by other workers for all
               texts in a task.

        Returns:
            Task-level agreement between reference annotators and workers.
        """
        ref_task_annotations = reference_task_annotations.annotations.items()
        agreements = []
        for text_passage_id, text_ref_annotations in ref_task_annotations:
            if text_passage_id in worker_task_annotations.annotations.keys():
                agreements.append(
                    self.get_text_reference_annotators_agreement(
                        text_ref_annotations,
                        worker_task_annotations.annotations[text_passage_id],
                    )
                )

        return sum(agreements) / len(agreements)
