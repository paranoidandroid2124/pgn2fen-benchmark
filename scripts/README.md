# Example Commands

## Generate FEN outputs for a specific model

```bash
python "scripts/run_model_on_benchmark.py" \
    --provider OPENAI \
    --model o3-mini-2025-01-31 \
    --extract_fen \
    --max_workers 10
```

## Inspect the results for a specific model

```bash
python "scripts/analyse_logs.py" \
    --input_file openai_o3-mini-2025-01-31 \
    --print_to_console \
    --output_file o3-mini-2025-01-31.txt
```

## Produce benchmark plots and tables

```bash
python "scripts/prepare_benchmark_results.py" \
    --evaluation-cols "full correctness" "piece placement" "turn" "castling" "en passant" "halfmove clock" "fullmove number"
```

