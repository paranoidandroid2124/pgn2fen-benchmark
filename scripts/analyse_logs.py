"""This script analyses PGN to FEN benchmark logs and generates formatted results."""

import argparse
from pathlib import Path

from pgn2fen.evaluate import get_counts_and_mean_n_halfmoves
from pgn2fen.pgn_io import load_experiments_from_jsonl

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def format_results(input_file, counts_and_means):
    """Format the analysis results into a string.

    Args:
        input_file (str): The name of the input file being analyzed.
        counts_and_means (tuple[dict, float]): A dictionary containing counts and a
            float for the mean halfmoves of each range.

    Returns:
        str: A formatted string of the analysis results.
    """
    output = [f"{input_file}\n"]

    for range_key, (counts, mean_halfmoves) in counts_and_means.items():
        output.append(
            f"Range: {range_key} moves (n={counts['n']}, mean_halfmoves={mean_halfmoves:.1f})"
        )

        for key in [
            "full_correctness",
            "piece_placement",
            "turn",
            "castling",
            "en_passant",
            "halfmove_clock",
            "fullmove_number",
        ]:
            count = counts[key]
            percentage = (count / counts["n"] * 100) if counts["n"] > 0 else 0
            output.append(f"    {key:16}: {count:4} ({percentage:.1f}%)")

        output.append("")

    return "\n".join(output)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyse PGN to FEN benchmark logs.")
    parser.add_argument(
        "--input_file",
        type=str,
        required=True,
        help="Name of the input JSONL file (without extension).",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        help="Optional output file to write results (in the 'results' folder).",
    )
    parser.add_argument(
        "--print_to_console",
        action="store_true",
        help="Print results to the console.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    input_file = args.input_file
    output_file = args.output_file
    print_to_console = args.print_to_console

    jsonl_file = PROJECT_ROOT / "model_logs" / f"{input_file}.jsonl"
    experiments = load_experiments_from_jsonl(jsonl_file)

    halfmove_ranges = [
        (1, 10),
        (11, 20),
        (21, 40),
        (41, 60),
        (61, 80),
        (81, 100),
    ]

    counts_and_means = {}
    for min_moves, max_moves in halfmove_ranges:
        range_key = f"{min_moves}-{max_moves}"
        counts, mean_n_halfmoves = get_counts_and_mean_n_halfmoves(
            experiments, min_halfmoves=min_moves, max_halfmoves=max_moves
        )
        counts_and_means[range_key] = (counts, mean_n_halfmoves)

    formatted_results = format_results(input_file, counts_and_means)

    if print_to_console:
        print(formatted_results)

    if output_file:
        results_path = PROJECT_ROOT / "results" / output_file
        with open(results_path, "w") as f:
            f.write(formatted_results)


if __name__ == "__main__":
    main()
