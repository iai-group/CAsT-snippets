# Data

## Preliminary study

The results of the preliminary study can be found [here](snippet_annotation/README.md).

### MTurk annotations

Annotations collected from crowdsourcing tasks run on Amazon Mechanical Turk are under [data/snippet_annotation/mturk](snippet_annotation/mturk/). They are divided into two subfolders containing paragraph-based annotations (under [data/snippet_annotation/mturk/paragraph](snippet_annotation/mturk/paragraph/)) and sentence-based annotations (under [data/snippet_annotation/mturk/sentence](snippet_annotation/mturk/sentence/)). Additionally, the results of relevant sentence selection subtask of sentence-based variant can be found under [data/relevant_sentence_selection/mturk](relevant_sentence_selection/mturk/). The filenames contain information about the task variant (1, 1a, 1b), the topic number (1, 2), and the type of workers (regular, master, expert): `subtask_{subtask_number}-topic_{topic_number}-paragraph/sentences-{worker_type}.csv`. Topic numbers correspond to the first two topics from the TREC CAsT'22 dataset (topic 1 corresponds to the topic with ID 132 and topic 2 corresponds to the topic with ID 133). There are three types of crowdsourcing tasks:
  * Subtask 1 - paragraph-based snippet annotation task
  * Subtask 1a - the first part of sentence-based annotation task, selecting relevant sentences
  * Subtask 1b - the second part of sentence-based annotation task, annotating snippets in relevant sentences

### Prolific annotations

Annotations collected from crowdsourcing tasks run on Prolific are under [data/snippet_annotation/prolific](snippet_annotation/prolific/). The filenames contain information about the topic number (1, 2): `prolific_topic_{topic_number}-paragraph.csv`. Similarly to MTurk annotations files, topic numbers correspond to the first two topics from the TREC CAsT'22 dataset.

## Large-scale data collection

Snippets annotations collected for TREC CAsT'20 and '22 are available under [data/large_scale/all](large_scale/all). They are divided into two subfolders containing paragraph-based annotations for CAsT'20 (under [data/large_scale/all/2020](large_scale/all/2020)) and CAsT'22 (under [data/large_scale/all/2022](large_scale/all/2022)). Additionally, a copy of the two sample topics used in our preliminary study that were annotated one more time in the large-scale data annotation process along with a copy of expert annotations can be found under [data/large_scale/topics_1-2](large_scale/topics_1-2). The filenames contain information about the batch and the group of crowdworkers assigned to it. Each file contains annotations done by 3 crowdworkers for 1-2 topics. All the annotations aggregated in one file can be found [here](large_scale/all/snippets_data_partitions.csv) along with information about train-validation-test split. The annotations are split across topics and not queries to avoid information leakage (5 topics in test partition (~12%), 5 topics in validation partition (~10%), and 32 topics in train partition (~78%)).
