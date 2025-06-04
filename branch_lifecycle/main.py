import sys
import json
from datetime import timedelta

from branch_lifecycle.lifecycle import get_branch_lifecycle
from branch_lifecycle.serializer import serialize_results, deserialize_results
from branch_lifecycle.analyzer import analyze_and_print_outliers
from branch_lifecycle.utils import load_config, format_duration  # <-- Add this import

def main():
    config = load_config('config/config.yaml')  # always load config.yaml

    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = config.get('repo_path', '.')

    print(f"Analyzing repo at: {repo_path}")

    base_branch = config.get('base_branch', 'develop')
    feature_prefixes = config.get('feature_prefixes', ['feature/', 'bugfix/', 'hotfix/', 'features/', 'fix/'])
    results_file = config.get('results_file', 'results.json')
    include_outlier_percent = config.get('include_outlier_percent', 50)

    results = []
    try:
        results = deserialize_results(results_file)
        if results:
            print(f"Loaded cached results: {len(results)} entries")
        else:
            print("Cache file empty or invalid, will recompute...")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"No cache file found or invalid ({e}), computing results...")

    # If results is empty after attempting to load, compute and save
    if not results:
        results = get_branch_lifecycle(repo_path, base_branch=base_branch, feature_prefixes=feature_prefixes)
        if results:
            serialize_results(results, results_file)
            print(f"Computed and saved results: {len(results)} entries")
        else:
            print("No results computed from branch lifecycle analysis.")

    if not results:
        print("No data to analyze.")
        return

    print(f"Preparing to analyze {len(results)} results...")

    duration_tuples = [(r['branch'], r['duration']) for r in results]

    filtered_results = analyze_and_print_outliers(duration_tuples, include_outlier_percent=include_outlier_percent)

    if filtered_results:
        total_filtered_duration = sum((dur for _, dur in filtered_results), timedelta())
        count = len(filtered_results)
        avg_duration = total_filtered_duration / count
        print(f"\n🎯 Average duration (excluding outliers, {count} branches): "
              f"{format_duration(avg_duration)}")
    else:
        print("No filtered results after outlier analysis.")

if __name__ == '__main__':
    main()
