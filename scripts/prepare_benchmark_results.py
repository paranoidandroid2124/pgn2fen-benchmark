"""Prepares benchmark results and visualisations for PGN2FEN experiments"""

from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import pandas as pd

from pgn2fen.evaluate import get_counts_and_mean_n_halfmoves
from pgn2fen.models import PGN2FENExperiment
from pgn2fen.pgn_io import load_experiments_from_jsonl


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_TYPE_TO_FILES = {
    "reasoning": [
        "openai_o3-mini-2025-01-31",
        "openai_o4-mini-2025-04-16",
        "openai_o3-2025-04-16",
        "google_gemini-2.5-pro-preview-03-25",
        "google_gemini-2.5-flash-preview-04-17",
        "deepseek_deepseek-reasoner",
    ],
    "non_reasoning": [
        "openai_gpt-4.1-nano-2025-04-14",
        "openai_gpt-4.1-mini-2025-04-14",
        "openai_gpt-4.1-2025-04-14",
        "google_gemini-2.0-flash-lite-001",
        "google_gemini-2.0-flash-001",
        "deepseek_deepseek-chat",
    ],
}


def prepare_table(
    json_files: list[Path],
    evaluation_col: str = "all correct",
    strata: list[tuple[int, int]] | None = None,
    output_string: str | None = None,
) -> pd.DataFrame:
    """
    Prepares a table summarising evaluation metrics for PGN2FEN experiments.

    Args:
        json_files (list[Path]): List of paths to JSONL files containing experiment logs.
        evaluation_col (str): The evaluation metric to calculate (default: "all correct").
        strata (list[tuple[int, int]] | None): List of move ranges for stratified analysis.
        output_string (str | None): Base name for output CSV and Markdown files.

    Returns:
        pd.DataFrame: DataFrame containing evaluation results.
    """
    if strata is None:
        strata = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 100)]

    evaluation_cols = [
        f"{evaluation_col} ({strata[i][0]}-{strata[i][1]} moves)" for i in range(len(strata))
    ]
    df = pd.DataFrame(columns=["provider", "model", *evaluation_cols])
    for json_file in json_files:
        experiments: list[PGN2FENExperiment] = load_experiments_from_jsonl(json_file)

        pcts_dict = {}
        for stratum in strata:
            counts, _ = get_counts_and_mean_n_halfmoves(
                experiments,
                min_halfmoves=stratum[0],
                max_halfmoves=stratum[1],
            )

            if counts["n"] == 0:
                pcts_dict[stratum] = None
            else:
                pcts_dict[stratum] = round(
                    counts[evaluation_col.lower().replace(" ", "_")] / counts["n"] * 100, 1
                )

        provider = experiments[0].llm_info.provider
        model = experiments[0].llm_info.model
        row = {
            "provider": provider,
            "model": model,
            **{
                f"{evaluation_col} ({stratum[0]}-{stratum[1]} moves)": pcts_dict[stratum]
                for stratum in strata
            },
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    df = df.sort_values(
        by=evaluation_cols,
        ascending=False,
    )

    if output_string:
        df_ = df.copy()
        evaluation_cols = [f"{strata[i][0]}-{strata[i][1]} moves" for i in range(len(strata))]
        df_.columns = ["provider", "model", *evaluation_cols]
        df_.to_csv(
            PROJECT_ROOT / "results" / f"{output_string}.csv",
            index=False,
        )
        df_.to_markdown(
            PROJECT_ROOT / "results" / f"{output_string}.md",
            index=False,
        )
    return df


def prepare_bar_plot(
    df: pd.DataFrame,
    strata: list[tuple[int, int]],
    evaluation_col: str,
    output_string: str = "bar_plot",
    model_type: str = "",
) -> None:
    """
    Creates a bar plot visualising evaluation metrics for PGN2FEN experiments.

    Args:
        df (pd.DataFrame): DataFrame containing evaluation results.
        strata (list[tuple[int, int]]): List of move ranges for stratified analysis.
        evaluation_col (str): The evaluation metric to visualise.
        output_string (str): Base name for the output PNG file (default: "bar_plot").
        model_type (str): Type of model (e.g., "reasoning" or "non_reasoning") for labeling.

    Returns:
        None
    """
    colours = []
    providers = {
        "google": [0, ["#3367D6", "#5C9DFF", "#4285F4", "#174EA6", "#0B3D91", "#7BAAF7"]],
        "openai": [0, ["#8E59FF", "#C084FC", "#5E2CA5", "#B266FF"]],
        "deepseek": [0, ["#00A88E", "#00D1C1", "#00BFAE", "#008578"]],
        "anthropic": [0, ["#E6AC00", "#FF9900", "#FFB800", "#CC8800"]],
    }
    for provider, model in zip(df["provider"], df["model"], strict=False):
        try:
            colours.append(providers[provider][1][providers[provider][0]])
            providers[provider][0] += 1
        except IndexError as e:
            raise ValueError(f"Too many models for provider {provider} (model: {model})") from e
        except KeyError as e:
            raise ValueError(f"Unknown provider: {provider} (model: {model})") from e

    if model_type:
        model_type = f" ({model_type.replace("_", "-").title()} Models)"

    df_ = df.copy()
    df_ = df_.fillna(0)
    df_ = df_.set_index(["provider", "model"])

    plt.rcParams.update({"font.size": 14})
    fig, ax = plt.subplots(figsize=(10, 7))
    df_.T.plot(kind="bar", ax=ax, color=colours)
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 100)
    ax.set_xticklabels([f"{stratum[0]}-{stratum[1]}\nmoves" for stratum in strata], rotation=45)
    ax.grid(axis="y", linestyle="--")
    ax.set_title(f"{evaluation_col.title()} Evaluation{model_type}")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)

    plt.tight_layout()
    plt.savefig(PROJECT_ROOT / "results" / f"{output_string}.png")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Prepare benchmark results and visualizations.")
    parser.add_argument(
        "--evaluation-cols",
        nargs="+",
        default=["full correctness", "piece placement"],
        help="List of evaluation columns to use (default: ['full correctness', 'piece placement'])",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    evaluation_cols = args.evaluation_cols
    strata = [(0, 10), (11, 20), (21, 40), (41, 60), (61, 80), (81, 100)]

    input_dir = PROJECT_ROOT / "model_logs"

    for model_type, model_files in MODEL_TYPE_TO_FILES.items():
        for evaluation_col in evaluation_cols:
            json_files = [input_dir / f"{file}.jsonl" for file in model_files]
            output_string = "_".join([evaluation_col.replace(" ", "_"), model_type])

            # Prepare data for analysis
            df = prepare_table(json_files, evaluation_col, strata, output_string)

            # Visualise results as a bar plot
            prepare_bar_plot(df, strata, evaluation_col, output_string, model_type)


if __name__ == "__main__":
    main()
