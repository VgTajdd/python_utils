#!/bin/bash

# Path to the Python script
python_script="merge_pdfs.py"

# Parameter for the script
parameter="./dir"

# Check if the Python script exists
if [ -f "$python_script" ]; then
    # Run the Python script with the parameter
    python3 "$python_script" "$parameter"
else
    echo "Error: $python_script not found."
fi
