"""Creates mapping between original and artificial worker ids.

Original worker ids are mapped to artificial ones in order to anonymize the
data. The original worker ids are stored in restricted access file
`https://docs.google.com/spreadsheets/d/1HlkgE0WNeKSopRMsu997BS_FMlofre76FfFGBmUT2v8/edit?usp=sharing`.
"""

import os

import pandas as pd

if __name__ == "__main__":
    unique_worker_ids = set()
    files_to_process = []

    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                annotated_data = pd.read_csv(file_path)
                if "WorkerId" in annotated_data.columns:
                    files_to_process.append(file_path)
                    unique_worker_ids.update(list(annotated_data["WorkerId"]))

    unique_worker_ids_mapping = {
        worker_id: "worker_{}".format(worker_id_mapping)
        for worker_id, worker_id_mapping in zip(
            unique_worker_ids, range(len(unique_worker_ids))
        )
    }
    unique_worker_ids_mapping_pd = pd.DataFrame(
        {
            "WorkerId": list(unique_worker_ids_mapping.keys()),
            "WorkerIdMapping": list(unique_worker_ids_mapping.values()),
        }
    )
    unique_worker_ids_mapping_pd.to_csv(
        "data/unique_worker_ids_mapping.csv", index=False
    )

    for file_path in files_to_process:
        annotated_data = pd.read_csv(file_path)
        annotated_data["WorkerId"] = annotated_data["WorkerId"].apply(
            lambda x: unique_worker_ids_mapping[x]
        )
        annotated_data.to_csv(file_path, index=False)
