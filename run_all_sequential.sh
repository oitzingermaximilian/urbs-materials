#!/bin/bash
echo "Starting all LR scenarios in parallel..."
echo "Start time: $(date)"

for lr in LR1 LR3_5 LR4 LR5 LR6 LR7 LR8 LR9 LR10 LR25; do
    echo ""
    echo "========================================"
    echo "Running $lr at $(date)"
    echo "========================================"
    python run_model.py --mode perfect --lr $lr
done

echo ""
echo "All learning rates completed at $(date)!"
