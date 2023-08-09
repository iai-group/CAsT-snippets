"""Helper functions for tests."""

from typing import List

from snippet_annotation.annotation import (
    InputText,
    Interval,
    TaskAnnotations,
    WorkerAnnotation,
    WorkerType,
)


def create_annotations_from_intervals(
    workers_intervals: List[List[Interval]],
) -> List[WorkerAnnotation]:
    """Creates a list of worker annotations from lists of intervals.

    Args:
        workers_intervals: Annotations done by several different workers in a
           given group for a single input text.

    Returns:
        List of workers' annotations.
    """
    return [
        WorkerAnnotation(
            intervals=interval,
            input_text=None,
            worker_id=None,
        )
        for interval in workers_intervals
    ]


def create_task_annotations_from_intervals(
    input_texts: List[InputText],
    intervals: List[List[Interval]],
    worker_type: WorkerType,
) -> TaskAnnotations:
    """Creates task annotations from lists of intervals and input texts.

    Args:
        input_texts: List of input texts for annotation task.
        intervals: Intervals chosen by several different workers in a given
           group for multiple input texts.
        worker_type: Type of workers working on a task.

    Returns:
        Task annotations.
    """
    return TaskAnnotations(
        annotations={
            (
                input_text.query_id,
                input_text.text_id,
            ): create_annotations_from_intervals(worker_annotations)
            for (input_text, worker_annotations) in zip(input_texts, intervals)
        },
        worker_type=worker_type,
    )
