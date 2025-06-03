import git
import json
import numpy as np
from datetime import datetime, timedelta

def get_branch_lifecycle(repo_path='.', base_branch='develop', feature_prefixes=None):
    if feature_prefixes is None:
        feature_prefixes = ['feature/', 'bugfix/', 'hotfix/', 'features/', 'fix/']

    repo = git.Repo(repo_path)
    base = repo.heads[base_branch]

    total_commits = int(repo.git.rev_list('--count', base_branch))
    print(f"Analyzing up to {total_commits} commits in branch '{base_branch}'...")

    branches_info = {}
    seen_branches = set()

    for merge_commit in repo.iter_commits(base_branch, max_count=total_commits):
        if len(merge_commit.parents) < 2:
            continue

        merged_branch_tip = merge_commit.parents[1]
        merge_bases = repo.merge_base(base.commit, merged_branch_tip)
        if not merge_bases:
            continue
        merge_base = merge_bases[0]

        branch_name = None
        for ref in repo.references:
            if ref.commit == merged_branch_tip and any(
                    ref.name.startswith(f'refs/heads/{prefix}') or
                    ref.name.startswith(prefix) or
                    ref.name.endswith(ref.name)
                    for prefix in feature_prefixes):
                branch_name = ref.name.replace('refs/heads/', '').replace('refs/remotes/origin/', '')
                break

        if not branch_name:
            msg = merge_commit.message.lower()
            for prefix in feature_prefixes:
                if prefix in msg:
                    branch_name = prefix + msg.split(prefix)[1].split()[0]
                    break

        if not branch_name:
            continue

        branch_name = branch_name.lower()

        if not any(branch_name.startswith(prefix) for prefix in feature_prefixes):
            continue

        if branch_name not in seen_branches:
            print(f"Analyzing merged branch: {branch_name} (Merge commit: {merge_commit.hexsha[:8]})")
            seen_branches.add(branch_name)

        created_at = datetime.fromtimestamp(merge_base.committed_date)
        merged_at = datetime.fromtimestamp(merge_commit.committed_date)

        if branch_name not in branches_info:
            branches_info[branch_name] = {'created_at': created_at, 'merged_at': merged_at}
        else:
            if created_at < branches_info[branch_name]['created_at']:
                branches_info[branch_name]['created_at'] = created_at
            if merged_at > branches_info[branch_name]['merged_at']:
                branches_info[branch_name]['merged_at'] = merged_at

    results = []
    total_duration = timedelta(0)
    count = 0

    for branch, info in branches_info.items():
        created_at = info['created_at']
        merged_at = info['merged_at']
        if merged_at < created_at:
            continue

        duration = merged_at - created_at
        total_duration += duration
        count += 1

        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        results.append({
            'branch': branch,
            'created_at': created_at,
            'merged_at': merged_at,
            'duration_days': days,
            'duration_hours': hours,
            'duration_minutes': minutes,
            'duration_seconds': duration.total_seconds(),
        })

    results.sort(key=lambda r: r['created_at'])

    for r in results:
        print(f"Branch: {r['branch']}, Created: {r['created_at']}, Merged: {r['merged_at']}, "
              f"Duration: {r['duration_days']} days, {r['duration_hours']} hours, {r['duration_minutes']} minutes")

    if count > 0:
        avg_duration = total_duration / count
        avg_days = avg_duration.days
        avg_hours, remainder = divmod(avg_duration.seconds, 3600)
        avg_minutes, _ = divmod(remainder, 60)
        print(f"\nAverage duration across {count} branches: {avg_days} days, {avg_hours} hours, {avg_minutes} minutes")
    else:
        print("No branches found to calculate average duration.")

    return results

def analyze_and_print_outliers(results, include_outlier_percent=50):
    if not results:
        print("No data to analyze.")
        return []

    durations_hours = [r[1].total_seconds() / 3600 for r in results]
    Q1 = np.percentile(durations_hours, 25)
    Q3 = np.percentile(durations_hours, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    print(f"Q1={Q1:.2f} hours, Q3={Q3:.2f} hours, IQR={IQR:.2f} hours")
    print(f"Lower bound for outliers: {lower_bound:.2f} hours")
    print(f"Upper bound for outliers: {upper_bound:.2f} hours\n")

    sorted_by_duration = sorted(results, key=lambda x: x[1])

    print("Top 100 shortest durations:")
    for name, dur in sorted_by_duration[:100]:
        days, hours, minutes = dur.days, dur.seconds // 3600, (dur.seconds % 3600) // 60
        print(f"- Branch '{name}': {days}d {hours}h {minutes}m")

    print("\nTop 100 longest durations:")
    for name, dur in sorted_by_duration[-100:][::-1]:
        days, hours, minutes = dur.days, dur.seconds // 3600, (dur.seconds % 3600) // 60
        print(f"- Branch '{name}': {days}d {hours}h {minutes}m")

    outliers = [(name, dur) for name, dur in results if dur.total_seconds() / 3600 < lower_bound or dur.total_seconds() / 3600 > upper_bound]

    total_outliers = len(outliers)
    print(f"\nFound {total_outliers} outlier branches")

    num_to_include = int((include_outlier_percent / 100.0) * total_outliers)
    outliers_sorted = sorted(outliers, key=lambda x: x[1].total_seconds(), reverse=True)
    included_outliers = set(outliers_sorted[:num_to_include])

    print(f"Including top {include_outlier_percent}% of outliers: {num_to_include} branches")

    filtered = [
        (name, dur) for (name, dur) in results
        if (lower_bound <= dur.total_seconds() / 3600 <= upper_bound) or (name, dur) in included_outliers
    ]

    if not filtered:
        print("No branches left after filtering to compute average.")
        return []

    total_duration = sum((dur for _, dur in filtered), timedelta())
    avg_duration = total_duration / len(filtered)
    avg_days = avg_duration.days
    avg_hours, remainder = divmod(avg_duration.seconds, 3600)
    avg_minutes, _ = divmod(remainder, 60)

    print(f"\n🎯 Average duration including top {include_outlier_percent}% outliers "
          f"({len(filtered)} branches): {avg_days} days, {avg_hours} hours, {avg_minutes} minutes")

    return filtered

def serialize_results(results, filename='results.json'):
    def converter(o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, timedelta):
            return o.total_seconds()
        raise TypeError(f"Type {type(o)} not serializable")

    with open(filename, 'w') as f:
        json.dump(results, f, default=converter, indent=2)

def deserialize_results(filename='results.json'):
    with open(filename, 'r') as f:
        data = json.load(f)

    results = []
    for item in data:
        # Convert datetime strings back to datetime objects
        created_at = datetime.fromisoformat(item['created_at'])
        merged_at = datetime.fromisoformat(item['merged_at'])

        # Rebuild timedelta from seconds
        duration_seconds = item['duration_seconds']
        duration = timedelta(seconds=duration_seconds)

        # We can optionally double-check or recompute days/hours/minutes if you want consistency:
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        results.append({
            'branch': item['branch'],
            'created_at': created_at,
            'merged_at': merged_at,
            'duration_days': days,
            'duration_hours': hours,
            'duration_minutes': minutes,
            'duration_seconds': duration_seconds,
            'duration': duration
        })
    return results

if __name__ == '__main__':
    import sys
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'

    try:
        results = deserialize_results('results.json')
        print("Loaded cached results")
    except FileNotFoundError:
        results = get_branch_lifecycle(repo_path)
        serialize_results(results, 'results.json')
        print("Computed and saved results")

    duration_tuples = [(r['branch'], r['duration']) for r in results]

    filtered_results = analyze_and_print_outliers(duration_tuples, include_outlier_percent=50)

    if filtered_results:
        total_filtered_duration = sum((dur for _, dur in filtered_results), timedelta())
        count = len(filtered_results)
        avg_duration = total_filtered_duration / count
        avg_days = avg_duration.days
        avg_hours, remainder = divmod(avg_duration.seconds, 3600)
        avg_minutes, _ = divmod(remainder, 60)

        print(f"\n🎯 Average duration (excluding outliers, {count} branches): "
              f"{avg_days} days, {avg_hours} hours, {avg_minutes} minutes")
