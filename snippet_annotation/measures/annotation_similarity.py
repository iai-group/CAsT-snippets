"""Abstract class for annotation similarity measures."""

from abc import ABC, abstractmethod
from typing import List

from snippet_annotation.annotation import TaskAnnotations, WorkerAnnotation


class WorkerAnnotationSimilarity(ABC):
    """Abstract class for annotation similarity measures."""

    @abstractmethod
    def get_text_annotation_similarity(
        self, annotations: List[WorkerAnnotation]
    ) -> float:
        """Computes the similarity between different workers annotations.

        Args:
            annotations: List of annotations made by several workers for the
               same input text.

        Returns:
            Similarity measure between multiple annotations.
        """
        raise NotImplementedError

    def get_task_inter_annotator_agreement(
        self, task_annotations: TaskAnnotations
    ) -> float:
        """Computes the inter-annotator agreement for an entire task.

        Args:
            task_annotations: Annotations made by several workers for all texts
               in a task.

        Returns:
            Task-level inter-annotator agreement.
        """
        similarities = [
            self.get_text_annotation_similarity(workers_annotations)
            for workers_annotations in task_annotations.annotations.values()
        ]

        return sum(similarities) / len(similarities)
