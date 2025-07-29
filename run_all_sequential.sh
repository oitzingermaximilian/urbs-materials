#!/bin/bash
echo "Starting all LR scenarios sequentially..."
echo "Start time: $(date)"

for lr in LR1 LR3_5 LR4 LR5 LR6 LR7 LR8 LR9 LR10 LR25; do
    echo ""
    echo "========================================"
    echo "Running $lr at $(date)"
    echo "========================================"
    python run_model.py --mode rolling --lr $lr
    echo "$lr completed at $(date)"
done

echo ""
echo "All learning rates completed at $(date)!"
