"""Main methods for generating LaTeX tables with values of measures."""

import os
import os.path
from typing import Dict, List, Tuple

import pandas as pd

from snippet_annotation.annotation import (
    ConfidenceScore,
    QueryPassage,
    TaskAnnotations,
    TaskVariant,
    WorkerType,
)
from snippet_annotation.measures.jaccard import Jaccard, JaccardLenient
from snippet_annotation.measures.rouge import Rouge, RougeMeasure, RougeVariant
from snippet_annotation.utilities.conversion import (
    AnnotationSource,
    convert_paragraph_task_annotation_to_sentence_based,
)
from snippet_annotation.utilities.data_loader import (
    load_confidence_values_from_file,
    load_worker_annotations_from_file,
)


def _get_jaccard_results(
    task_annotations: TaskAnnotations, k_values: List[int]
) -> Tuple[float, Dict[int, float]]:
    """Computes Jaccard measures for task annotations.

    Args:
        task_annotations: All annotations collected in a crowdsourcing task
          (possibly for multiple topics).
        k_values: Values of k for lenient variant of Jaccard agreement.

    Returns:
        Values of Jaccard measures. First element of a tuple is value of strict
        variant of the measure. Second element of the tuple is a dictionary with
        values of lenient variant of the measure for every k.
    """
    jaccard = Jaccard()
    jaccard_agreement = round(
        jaccard.get_task_inter_annotator_agreement(task_annotations), 2
    )
    jaccard_k_agreements = {}
    for k in k_values:
        jaccard_n = JaccardLenient(k=k)
        jaccard_k_agreements[k] = round(
            jaccard_n.get_task_inter_annotator_agreement(task_annotations), 2
        )

    return jaccard_agreement, jaccard_k_agreements


def _get_rouge_measures_results(
    reference_task_annotations: TaskAnnotations,
    worker_task_annotations: TaskAnnotations,
) -> Dict[RougeMeasure, float]:
    """Computes Rouge measures for task annotations.

    Args:
        reference_task_annotations: Reference annotations made for all texts in
          a task.
        worker_task_annotations: Annotations made by other workers for all texts
          in a task.

    Returns:
        Dictionary with values of Rouge measures.
    """
    rouge_measures = {}
    for rouge_measure in RougeMeasure:
        rouge = Rouge(
            rouge_measure=rouge_measure, rouge_variant=RougeVariant.MEAN
        )
        rouge_measures[rouge_measure] = round(
            rouge.get_task_reference_annotator_agreement(
                reference_task_annotations, worker_task_annotations
            ),
            2,
        )
    return rouge_measures


def _get_rouge_variants_results(
    reference_task_annotations: TaskAnnotations,
    worker_task_annotations: TaskAnnotations,
    n: int,
) -> Dict[RougeVariant, float]:
    """Computes F1 measure for different Rouge variants for task annotations.

    Args:
        reference_task_annotations: Reference annotations made for all texts in
          a task.
        worker_task_annotations: Annotations made by other workers for all texts
          in a task.
        n: The minimum amount of workers in the group that need to annotate an
          interval for majority ROUGE measure variant.

    Returns:
        Dictionary with values of F1 measure for different Rouge variants.
    """
    rouge_variants = {}
    for rouge_variant in RougeVariant:
        rouge = Rouge(
            rouge_measure=RougeMeasure.F1, rouge_variant=rouge_variant, n=n
        )
        rouge_variants[rouge_variant] = round(
            rouge.get_task_reference_annotator_agreement(
                reference_task_annotations, worker_task_annotations
            ),
            2,
        )
    return rouge_variants


def _aggregate_topics_annotations(
    topics_files_paths: List[str],
    worker_type: WorkerType,
    task_variant: TaskVariant,
) -> TaskAnnotations:
    """Combines annotations for multiple topics in one dictionary.

    Args:
        topics_files_paths: Paths to annotations files for different topics.
        worker_type: Type of the worker.
        task_variant: Variant of the task.

    Returns:
        One TaskAnnotations object with annotations aggregated from multiple
        topics.
    """
    topics_annotations = {}
    for topic_file in topics_files_paths:
        topic_annotations = load_worker_annotations_from_file(
            topic_file,
            AnnotationSource.PROLIFIC
            if worker_type == WorkerType.PROLIFIC
            else AnnotationSource.MTURK,
        )
        topics_annotations.update(topic_annotations)
    return TaskAnnotations(
        annotations=topics_annotations,
        worker_type=worker_type,
        sentence_based=task_variant == TaskVariant.SENTENCES,
    )


def get_rouge_results_as_dataframes(
    annotations_dir_path: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Creates two dataframes with values of Rouge measures.

    Measures are computed for all files in a given directory. Annotations for
    different topics are aggregated for the same type of annotation task.

    Args:
        annotations_dir_path: Path with annotations files.

    Returns:
        A dataframe with values of Rouge measures for all types of annotation
        task in the given directory and a dataframe with values of F1 measure
        for different variants of Rouge.
    """
    annotations_filenames = _get_filenames_from_subdirectories(
        annotations_dir_path
    )

    paragraph_expert_topic_files = [
        file
        for file in annotations_filenames
        if TaskVariant.PARAGRAPH.name.lower() in file
        and WorkerType.EXPERT.name.lower() in file
    ]
    paragraph_expert_annotations = _aggregate_topics_annotations(
        paragraph_expert_topic_files, WorkerType.EXPERT, TaskVariant.PARAGRAPH
    )
    sentence_expert_topics_annotations = {}
    for topic_file in paragraph_expert_topic_files:
        paragraph_topic_annotations = load_worker_annotations_from_file(
            topic_file,
            AnnotationSource.MTURK,
        )
        sentence_topic_annotations = (
            convert_paragraph_task_annotation_to_sentence_based(
                paragraph_topic_annotations
            )
        )
        sentence_expert_topics_annotations.update(sentence_topic_annotations)
    sentence_expert_annotations = TaskAnnotations(
        annotations=sentence_expert_topics_annotations,
        worker_type=WorkerType.EXPERT,
        sentence_based=True,
    )
    rouge_measures_values = []
    rouge_variants_values = []
    for task_variant in TaskVariant:
        for worker_type in [
            worker_type
            for worker_type in WorkerType
            if worker_type != WorkerType.EXPERT
        ]:
            topic_files = [
                file
                for file in annotations_filenames
                if task_variant.name.lower() in file
                and worker_type.name.lower().replace("mturk_", "") in file
            ]

            expert_annotations = (
                paragraph_expert_annotations
                if task_variant == TaskVariant.PARAGRAPH
                else sentence_expert_annotations
            )

            if len(topic_files) > 0:
                workers_annotations = _aggregate_topics_annotations(
                    topic_files, worker_type, task_variant
                )
                rouge_measures = _get_rouge_measures_results(
                    expert_annotations, workers_annotations
                )
                rouge_measures_values.append(
                    [
                        "{}-based".format(task_variant.name.lower()),
                        worker_type.name.lower().replace("_", " "),
                        rouge_measures[RougeMeasure.PRECISION],
                        rouge_measures[RougeMeasure.RECALL],
                        rouge_measures[RougeMeasure.F1],
                    ]
                )
                rouge_variants = _get_rouge_variants_results(
                    expert_annotations,
                    workers_annotations,
                    3 if task_variant == TaskVariant.PARAGRAPH else 2,
                )
                rouge_variants_values.append(
                    [
                        "{}-based".format(task_variant.name.lower()),
                        worker_type.name.lower().replace("_", " "),
                        rouge_variants[RougeVariant.MEAN],
                        rouge_variants[RougeVariant.MAJORITY],
                        rouge_variants[RougeVariant.SIMILARITY],
                    ]
                )

    rouge_measures_values_pd = pd.DataFrame(rouge_measures_values)
    rouge_measures_values_pd.columns = [
        "Task variant",
        "Annotator",
        "P",
        "R",
        "F1",
    ]

    rouge_variants_values_pd = pd.DataFrame(rouge_variants_values)
    rouge_variants_values_pd.columns = [
        "Task variant",
        "Annotator",
        "Mean F1",
        "Majority F1",
        "Similarity F1",
    ]

    return (rouge_measures_values_pd, rouge_variants_values_pd)


def _aggregate_confidence_scores(
    topics_files_paths: List[str],
) -> Dict[QueryPassage, List[ConfidenceScore]]:
    """Combines confidence scores for multiple topics in one dictionary.

    Args:
        topics_files_paths: Paths to annotations files for different topics.

    Returns:
        Dictionary indexed by input text id with lists of confidence scores for
        each passage and each worker in all topics files.
    """
    confidence_scores = {}
    for topic_file in topics_files_paths:
        topic_confidence_scores = load_confidence_values_from_file(topic_file)
        confidence_scores.update(topic_confidence_scores)
    return confidence_scores


def get_jaccard_and_confidence_score_results_as_dataframe(
    annotations_dir_path: str,
) -> pd.DataFrame:
    """Creates a dataframe with values of Jaccard similarity and confidence.

    Args:
        annotations_dir_path: Path with annotations files.

    Returns:
        Dataframe with values of Jaccard similarity and the average confidence
        scores.
    """
    annotations_filenames = _get_filenames_from_subdirectories(
        annotations_dir_path
    )

    jaccard = Jaccard()
    jaccard_values = {}
    confidence_scores_averages = {}

    topic_files = [file for file in annotations_filenames]
    if len(topic_files) > 0:
        task_annotations = _aggregate_topics_annotations(
            topic_files, WorkerType.MTURK_MASTER, TaskVariant.PARAGRAPH
        )
        task_confidence_scores = _aggregate_confidence_scores(topic_files)

        for query_passage, annotations in task_annotations.annotations.items():
            jaccard_values[
                query_passage
            ] = jaccard.get_text_annotation_similarity(annotations)

        for query_passage, confidence_scores in task_confidence_scores.items():
            confidence_scores_values = [
                score.value for score in confidence_scores
            ]
            confidence_scores_averages[query_passage] = sum(
                confidence_scores_values
            ) / len(confidence_scores_values)

    return pd.DataFrame(
        {
            "QueryPassage": jaccard_values.keys(),
            "Jaccard": jaccard_values.values(),
            "Confidence": confidence_scores_averages.values(),
        }
    )


def get_jaccard_results_as_dataframes(
    annotations_dir_path: str,
) -> pd.DataFrame:
    """Creates dataframe with values of Jaccard measures.

    Measures are computed for all files in a given directory. Annotations for
    different topics are aggregated for the same type of annotation task.

    Args:
        annotations_dir_path: Path with annotations files.

    Returns:
        Dataframe with values of Jaccard measures for all types of
        annotation task in the given directory.
    """
    annotations_filenames = _get_filenames_from_subdirectories(
        annotations_dir_path
    )

    jaccard_lenient_k_values = [4, 3, 2]

    jaccard_values = []
    for task_variant in TaskVariant:
        for worker_type in WorkerType:
            topic_files = [
                file
                for file in annotations_filenames
                if task_variant.name.lower() in file
                and worker_type.name.lower().replace("mturk_", "") in file
            ]
            if len(topic_files) > 0:
                task_annotations = _aggregate_topics_annotations(
                    topic_files, worker_type, task_variant
                )
                jaccard, jaccard_k = _get_jaccard_results(
                    task_annotations, jaccard_lenient_k_values
                )
                jaccard_values.append(
                    [
                        "{}-based".format(task_variant.name.lower()),
                        worker_type.name.lower().replace("_", " "),
                        jaccard,
                        jaccard_k[4],
                        jaccard_k[3],
                        jaccard_k[2],
                    ]
                )

    jaccard_values_pd = pd.DataFrame(jaccard_values)
    jaccard_values_pd.columns = [
        "Task variant",
        "Annotator",
        "Jaccard",
        "Jaccard_k=4",
        "Jaccard_k=3",
        "Jaccard_k=2",
    ]

    return jaccard_values_pd


def _get_filenames_from_subdirectories(dir_path: str):
    """Gets all filenames from subdirectories.

    Args:
        dir_path: Path to the directory.

    Returns:
        All filenames from subdirectories.
    """
    filenames = []
    for path, _, files in os.walk(dir_path):
        for filename in files:
            filenames.append(os.path.join(path, filename))
    return filenames


if __name__ == "__main__":
    print("*** Experimental results for two sample topics ***")
    jaccard_results = get_jaccard_results_as_dataframes(
        "data/snippet_annotation"
    )
    print(jaccard_results.to_latex(index=False))

    (
        rouge_measures_results,
        rouge_variants_results,
    ) = get_rouge_results_as_dataframes("data/snippet_annotation")

    print(rouge_measures_results.to_latex(index=False))
    print(rouge_variants_results.to_latex(index=False))

    print("*** Results of large-scale data annotation on two sample topics ***")

    jaccard_results = get_jaccard_results_as_dataframes(
        "data/large_scale/topics_1-2"
    )
    print(jaccard_results.to_latex(index=False))

    (
        rouge_measures_results,
        rouge_variants_results,
    ) = get_rouge_results_as_dataframes("data/large_scale/topics_1-2")

    print(rouge_measures_results.to_latex(index=False))
    print(rouge_variants_results.to_latex(index=False))

    print(
        "*** Results of large-scale data annotation on TREC CAsT'20 and '22 ***"
    )

    jaccard_results = get_jaccard_results_as_dataframes("data/large_scale/all")
    print(jaccard_results.to_latex(index=False))

    get_jaccard_and_confidence_score_results_as_dataframe(
        "data/large_scale/all"
    ).to_csv("data/large_scale/jaccard_confidence.csv")
