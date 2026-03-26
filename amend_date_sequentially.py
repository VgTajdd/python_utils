import subprocess
import sys
import os
import tempfile
from datetime import datetime, timedelta


def run_command(command, capture_output=False, env=None):
    """Runs a shell command."""
    try:
        if capture_output:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            return result.stdout.decode("utf-8").strip()
        else:
            subprocess.run(command, shell=True, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e}", file=sys.stderr)
        sys.exit(1)


def amend_commit_dates(initial_date, num_commits):
    # Validate initial_date format (YYYY-MM-DD)
    try:
        current_date = datetime.strptime(initial_date, "%Y-%m-%d")
    except ValueError:
        print("Error: Initial date must be in YYYY-MM-DD format.")
        sys.exit(1)

    # Get the last n commit hashes in reverse order (oldest first)
    commit_hashes = run_command(
        f"git rev-list HEAD~{num_commits}..HEAD --reverse", capture_output=True
    ).splitlines()

    if len(commit_hashes) != num_commits:
        print(
            f"Error: Specified number of commits ({num_commits}) exceeds the current branch history."
        )
        sys.exit(1)

    # Create a mapping of commit hash to new date
    commit_date_map = {}
    for i, commit_hash in enumerate(commit_hashes):
        new_date = current_date + timedelta(
            days=i
        )  # Increment by 1 day for each commit
        # Format with timezone (using local timezone offset)
        formatted_date = new_date.strftime("%a %b %d 12:00:00 %Y -0000")
        commit_date_map[commit_hash] = formatted_date
        print(f"Will amend commit {commit_hash[:8]} with date: {formatted_date}")

    # Create a temporary script for git filter-branch
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".sh", delete=False
    ) as script_file:
        script_file.write("#!/bin/bash\n")
        script_file.write("# Map commit hashes to dates\n")

        for commit_hash, date in commit_date_map.items():
            script_file.write(f'if [ "$GIT_COMMIT" = "{commit_hash}" ]; then\n')
            script_file.write(f'    export GIT_AUTHOR_DATE="{date}"\n')
            script_file.write(f'    export GIT_COMMITTER_DATE="{date}"\n')
            script_file.write("fi\n")

        script_file_path = script_file.name

    # Make the script executable
    os.chmod(script_file_path, 0o755)

    try:
        print(f"\nRewriting commit history for the last {num_commits} commits...")

        # Use git filter-branch to rewrite the commits
        env = os.environ.copy()
        run_command(
            f"FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f "
            f'--env-filter "source {script_file_path}" '
            f"HEAD~{num_commits}..HEAD",
            env=env,
        )

        print("\nSuccessfully amended commit dates.")
        print(
            "Note: This has rewritten git history. If you've already pushed these commits,"
        )
        print("you'll need to force push: git push --force")
    finally:
        # Clean up the temporary script
        os.unlink(script_file_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python amend_commit_dates.py <initial-date:YYYY-MM-DD> <number-of-commits>"
        )
        sys.exit(1)

    initial_date = sys.argv[1]
    num_commits = int(sys.argv[2])

    amend_commit_dates(initial_date, num_commits)
