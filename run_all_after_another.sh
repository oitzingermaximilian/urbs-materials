#!/bin/bash
echo "Starting all LR scenarios in parallel..."
echo "Start time: $(date)"

for lr in LR4; do
    echo ""
    echo "========================================"
    echo "Running $lr at $(date)"
    echo "========================================"
    python run_model.py --mode perfect --lr $lr
done

echo ""
echo "All learning rates completed at $(date)!"
