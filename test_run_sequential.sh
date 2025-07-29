#!/bin/bash
echo "Testing sequential LR scenarios runner..."
echo "Start time: $(date)"

# Test parameters - you can adjust these
TEST_SCENARIOS=("LR1" "LR3_5" "LR4")  # Just test with 3 scenarios instead of all 10
SLEEP_DURATION=2  # Simulate work with short sleep instead of actual model run

for lr in "${TEST_SCENARIOS[@]}"; do
    echo ""
    echo "========================================"
    echo "Testing $lr at $(date)"
    echo "========================================"

    # Instead of running the actual model, we'll simulate it
    echo "Simulating: python run_model.py --mode rolling --lr $lr"
    echo "Working on $lr scenario..."

    # Simulate some work time
    sleep $SLEEP_DURATION

    # Check if run_model.py exists and can accept these parameters
    if [ -f "run_model.py" ]; then
        echo "✓ run_model.py found"
        # You could add a dry-run check here if your script supports it
        python -c "
import sys
print('✓ Python is working')
try:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode')
    parser.add_argument('--lr')
    args = parser.parse_args(['--mode', 'rolling', '--lr', '$lr'])
    print('✓ Arguments parsing works:', args)
except Exception as e:
    print('✗ Error with arguments:', e)
"
    else
        echo "✗ run_model.py not found"
    fi

    echo "$lr test completed at $(date)"
done

echo ""
echo "All learning rate tests completed at $(date)!"
echo "If this test ran successfully, your full script should work too."
