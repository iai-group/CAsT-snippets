"""Utility functions for loading annotation data from files."""

import ast
from collections import defaultdict
from typing import Dict, List

import pandas as pd

from snippet_annotation.annotation import (
    ConfidenceScore,
    InputText,
    QueryPassage,
    WorkerAnnotation,
)
from snippet_annotation.utilities.conversion import (
    AnnotationSource,
    convert_worker_annotation_to_intervals,
)


def load_worker_annotations_from_file(
    task_data_path: str, source: AnnotationSource
) -> Dict[QueryPassage, List[WorkerAnnotation]]:
    """Loads all snippets annotations for a given task from file.

    Args:
        task_data_path: Path to the file with annotations for a task
            variant.
        source: Source of the annotation.

    Returns:
        Dictionary indexed by input text id with lists of worker annotations for
        each passage/sentence and each worker.
    """
    annotations = pd.read_csv(task_data_path, sep=",", encoding="utf-8")
    sentence_based = "Input.sentence_id" in annotations.columns
    snippet_annotations = defaultdict(list)
    for _, annotation in annotations.iterrows():
        intervals = convert_worker_annotation_to_intervals(
            annotation["Answer.taskAnswers"], sentence_based, source
        )
        turn_id = annotation["Input.turn_id"]
        text = (
            annotation["Input.sentence"]
            if sentence_based
            else annotation["Input.passage"]
        )
        text_id = (
            ast.literal_eval(annotation["Input.passage_id"])[0]
            if source == AnnotationSource.PROLIFIC
            else annotation["Input.sentence_id"]
            if sentence_based
            else annotation["Input.passage_id"]
        )
        input_text = InputText(
            query=annotation["Input.query"],
            query_id=turn_id,
            text=text,
            text_id=text_id,
        )
        worker_annotation = WorkerAnnotation(
            intervals=intervals,
            input_text=input_text,
            worker_id=annotation["WorkerId"],
        )
        snippet_annotations[(turn_id, text_id)].append(worker_annotation)

    return snippet_annotations


def load_confidence_values_from_file(
    task_data_path,
) -> Dict[QueryPassage, List[ConfidenceScore]]:
    """Loads confidence values for each worker and annotation from file.

    Args:
        task_data_path: Path to the file with annotations for a task
            variant.

    Returns:
        Dictionary indexed by input text id with lists of confidence scores for
        each passage and each worker.
    """
    annotations = pd.read_csv(task_data_path, sep=",", encoding="utf-8")
    confidence_scores = defaultdict(list)
    for _, annotation in annotations.iterrows():
        turn_id = annotation["Input.turn_id"]
        text_id = annotation["Input.passage_id"]
        answer_confidence = ast.literal_eval(annotation["Answer.taskAnswers"])[
            0
        ]["answer_confidence"]
        confidence_score_str = [k for k, v in answer_confidence.items() if v][0]
        confidence_score_str = ConfidenceScore[confidence_score_str.upper()]
        confidence_scores[(turn_id, text_id)].append(confidence_score_str)

    return confidence_scores
