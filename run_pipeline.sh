#!/bin/bash

# Change to project directory
cd /path/to/equity_research_pipeline  # Replace with actual path

# Run the pipeline
python src/main.py >> logs/pipeline.log 2>&1