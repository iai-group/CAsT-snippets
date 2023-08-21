# Towards Filling the Gap in Conversational Search: From Passage Retrieval to Conversational Response Generation

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![build](https://github.com/iai-group/CAsT-snippets/actions/workflows/python-package-conda.yaml/badge.svg)](https://github.com/iai-group/CAsT-snippets/actions/workflows/python-package-conda.yaml)
![Python version](https://img.shields.io/badge/python-3.9-blue)

This repository provides resources developed within the following article [[PDF](https://arxiv.org/abs/2308.08911)]:

> W. Łajewska and K. Balog. **Towards Filling the Gap in Conversational Search: From Passage Retrieval to Conversational Response Generation.** In: Proceedings of the 32nd ACM International Conference on Information and Knowledge Management (CIKM '23). ACM. Birmingham, United Kingdom. October 2023. [10.1145/3583780.3615132](https://doi.org/10.1145/3583780.3615132)

An extended version of this paper is available on [arXiv](https://arxiv.org/abs/2308.08911).

## Summary

Research on conversational search has so far mostly focused on query rewriting and multi-stage passage retrieval. However, synthesizing the top retrieved passages into a complete, relevant, and concise response is still an open challenge. Having snippet-level annotations of relevant passages would enable both (1) the training of response generation models that are able to ground answers in actual statements and (2) the automatic evaluation of the generated responses in terms of completeness. In this paper, we address the problem of collecting high-quality snippet-level answer annotations for two of the TREC Conversational Assistance track datasets. To ensure quality, we first perform a preliminary annotation study, employing different task designs, crowdsourcing platforms, and workers with different qualifications. Based on the outcomes of this study, we refine our annotation protocol before proceeding with the full-scale data collection. Overall, we gather annotations for 1.8k question-paragraph pairs, each annotated by three independent crowd workers. The process of collecting data at this magnitude also led to multiple insights about the problem that can inform the design of future response-generation methods.

## CAsT-snippets dataset

Snippets annotations collected for TREC CAsT'20 and '22 are available under [data/large_scale/all](data/large_scale/all). They are divided into two subfolders containing paragraph-based annotations for CAsT'20 (under [data/large_scale/all/2020](data/large_scale/all/2020)) and CAsT'22 (under [data/large_scale/all/2022](data/large_scale/all/2022)). Additionally, a copy of the two sample topics used in our preliminary study that were annotated one more time in the large-scale data annotation process along with a copy of expert annotations can be found under [data/large_scale/topics_1-2](data/large_scale/topics_1-2). The filenames contain information about the batch and the group of crowdworkers assigned to it. Each file contains annotations done by 3 crowdworkers for 1-2 topics. All the annotations aggregated in one file can be found [here](data/large_scale/all/snippets_data_partitions.csv) along with information about train-validation-test split (in total 1,855 query-passage pairs). The annotations are split across topics and not queries to avoid information leakage (5 topics in test partition (~12%), 5 topics in validation partition (~10%), and 32 topics in train partition (~78%)).

| Dataset | #queries | #passages per query | #annotators per passage | #query-passage pairs | Avg. snippet length (tokens) | #snippets per annotation |
| --- | --- | --- | --- | --- | --- | --- |
| CAsT-snippets | 371 | 5 | 3 | 1,855 | 39.6 | 2.3 |

The annotated data for every task configuration considered in the paper is covered in detail [here](data/README.md). 

![alt text](crowdsourcing_task_design/snippets_dataset_sample.png)

## Crowdsourcing task design

The crowdsourcing task designs and the automatic quality control mechanisms are covered in detail [here](crowdsourcing_task_design/README.md). 

## Evaluation measures

The implementation of similarity measures, both for inter-annotator agreement as well as for agreement between crowd workers and expert annotators, can be found [here](snippet_annotation/measures/). To generate the result tables presented in the paper run the following command:

``
python -m snippet_annotation.create_result_tables
``

## Citation

If you use the resources presented in this repository, please cite:

```
@inproceedings{Lajewska:2023:CIKM,
  author =    {Weronika Łajewska and Krisztian Balog},
  title =     {Towards Filling the Gap in Conversational Search: From Passage Retrieval to Conversational Response Generation},
  booktitle = {Proceedings of the 32nd ACM International Conference on Information and Knowledge Management},
  series =    {CIKM '23},
  year =      {2023},
  doi =       {10.1145/3583780.3615132},
  publisher = {ACM}
}
```

## Contact

Should you have any questions, please contact `Weronika Łajewska` at `weronika.lajewska`[AT]uis.no (with [AT] replaced by @).
