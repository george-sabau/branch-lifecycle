import git
from datetime import datetime, timedelta

def get_branch_lifecycle(repo_path='.', base_branch='develop', feature_prefixes=None):
    if feature_prefixes is None:
        feature_prefixes = ['feature/', 'bugfix/', 'hotfix/', 'features/', 'fix/']

    repo = git.Repo(repo_path)

    # Check base branch presence (optional but recommended)
    if base_branch not in repo.heads:
        raise ValueError(f"Base branch '{base_branch}' not found.")

    base = repo.heads[base_branch]

    total_commits = int(repo.git.rev_list('--count', base_branch))
    print(f"Analyzing up to {total_commits} commits in branch '{base_branch}'...")

    branches_info = {}
    seen_branches = set()

    for merge_commit in repo.iter_commits(base_branch, max_count=total_commits):
        if len(merge_commit.parents) < 2:
            continue

        # Extract author info from merge commit
        author_name = merge_commit.author.name
        author_email = merge_commit.author.email

        # Get merge base
        merged_branch_tip = merge_commit.parents[1]
        merge_bases = repo.merge_base(base.commit, merged_branch_tip)
        if not merge_bases:
            continue
        merge_base = merge_bases[0]

        branch_name = None
        for ref in repo.references:
            ref_name = ref.name
            if ref.commit == merged_branch_tip and any(
                    ref_name.startswith(f'refs/heads/{prefix}') or
                    ref_name.startswith(prefix) or
                    ref_name.endswith(ref_name)
                    for prefix in feature_prefixes):
                branch_name = ref_name.replace('refs/heads/', '').replace('refs/remotes/origin/', '')
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
            branches_info[branch_name] = {
                'created_at': created_at,
                'merged_at': merged_at,
                'author_name': author_name,
                'author_email': author_email,
            }
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
            'duration': duration,
            'author_name': info.get('author_name', ''),
            'author_email': info.get('author_email', ''),
        })

    results.sort(key=lambda r: r['created_at'])

    return results