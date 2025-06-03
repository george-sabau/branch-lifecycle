import git

repo = git.Repo('/Users/ges/rwa/rwahybris')
base_branch = 'develop'

print(f"Branches found:")
for b in repo.branches:
    print(f" - {b}")

print(f"\nMerge commits on {base_branch}:")
for commit in repo.iter_commits(base_branch, max_count=20):
    if len(commit.parents) > 1:
        print(f" - {commit.hexsha[:8]}: {commit.message.strip()}")

print(f"\nBranches matching prefixes:")
feature_prefixes = ['feature/', 'bugfix/', 'hotfix/', 'features/', 'fix/']
for ref in repo.references:
    if any(ref.name.startswith(f'refs/heads/{p}') for p in feature_prefixes):
        print(f" - {ref.name}")
