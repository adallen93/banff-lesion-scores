"""glomerulosclerosis.py.

This script provides functions to calculate Glomerulosclerosis (GS), which is
the proportion of scarred glomeruli.


The functions rely on biopsy data—such as counts of total vs. sclerotic
glomeruli and estimated areas of fibrosis—and return standardized numeric
scores. Researchers and clinicians can use these results to evaluate
allograft status and track progression of chronic injury.

Usage:
    1. Import this script or call the functions directly to compute
       individual lesion scores:

         from banff_lesion_scores import calculate_gs

         gs_score = calculate_gs(total_glomeruli, sclerotic_glomeruli)

    2. Integrate the lesion scores into broader diagnostic workflows.
       Reference the Banff classification guidelines for score
       interpretation and reporting.

Functions:
    - calculate_gs(UPDATE) -> float:
        Calculates the proportion of glomeruli affected by sclerosis
        (glomerulosclerosis).

Reference:
    For further details on the Banff classification and lesion scoring
    criteria, consult the Banff Working Group publications and relevant
    nephropathology guidelines.

Disclaimer:
    These implementations are provided for research and educational
    purposes. Clinical decisions should be based on professional medical
    judgment and corroborated by multiple sources of information.

Author:
    Austin Allen, Kitware, Inc., 2025
"""

# import csv
import json
from typing import Any

import numpy as np
import scipy.stats as stats
from slicer_cli_web import CLIArgumentParser


def compute_gs(
    non_globally_sclerotic_glomeruli: dict[str, Any],
    globally_sclerotic_glomeruli: dict[str, Any],
) -> dict[str, Any]:
    """Compute Glomerulosclerosis.

    Args:
    non_globally_sclerotic_glomeruli (): JSON annotations for NGSG.
    globally_sclerotic_glomeruli (): JSON annotations for GSG.

    Returns (float): Proportion of glomeruli that have global sclerosis.
    """
    count_ngsg = len(
        non_globally_sclerotic_glomeruli["annotation"]["elements"]
    )
    count_gsg = len(globally_sclerotic_glomeruli["annotation"]["elements"])
    n = count_ngsg + count_gsg

    # Compute proportion of GSG
    gsg_proportion = count_gsg / n

    # Compute 95% confidence interval
    lower_bound = gsg_proportion + stats.norm.ppf(0.025) * np.sqrt(
        gsg_proportion * (1 - gsg_proportion) / n
    )
    upper_bound = gsg_proportion + stats.norm.ppf(0.975) * np.sqrt(
        gsg_proportion * (1 - gsg_proportion) / n
    )
    confidence_interval = f"[{round(lower_bound, 4)}, {round(upper_bound, 4)}]"

    return {
        "Glomeruli Seen": n,
        "Glomeruli Sclerosed #": count_gsg,
        "Glomeruli Sclerosed %": round(gsg_proportion, 4),
        "95% Confidence Interval": confidence_interval,
    }


def main(configs: dict[str, str]) -> None:
    """Main."""
    print(configs)
    # Load annotations using JSON
    with open(configs.non_gsg_file) as file:
        ngsg = json.load(file)
    with open(configs.gsg_file) as file:
        gsg = json.load(file)

    # Compute GS
    gs = compute_gs(ngsg, gsg)

    # Print report
    header = " " * 5 + "REPORT" + " " * 5 + "\n"
    bar = "#" * 16 + "\n"
    print(header + bar)
    for key, value in gs.items():
        print(f"{key}: {value}")

    # # Save results to results-folder location (defaults to CWD)
    # with open(
    #     f"{configs['results_directory']}/glomerulosclerosis.csv",
    #     "w",
    #     newline="",
    # ) as file:
    #     # Use the CSV dictionary writer to store the results in the specified
    #     # directory
    #     writer = csv.DictWriter(file, fieldnames=gs.keys())
    #     writer.writeheader()
    #     writer.writerow(gs)


if __name__ == "__main__":
    configs = CLIArgumentParser().parse_args()
    main(configs)
