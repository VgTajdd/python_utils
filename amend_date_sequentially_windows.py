import os
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta


def run_command(command, capture_output=False, env=None):
    """Run a command and return stdout when requested."""
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=capture_output,
            text=True,
            env=env,
        )
        if capture_output:
            return result.stdout.strip()
        return None
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as error:
        rendered_command = " ".join(command)
        stderr_output = (error.stderr or "").strip()
        print(f"Error running command: {rendered_command}", file=sys.stderr)
        if stderr_output:
            print(stderr_output, file=sys.stderr)
        sys.exit(1)


def windows_path_to_posix(path):
    path = path.replace("\\", "/")
    if len(path) >= 2 and path[1] == ":":
        drive = path[0].lower()
        path = f"/{drive}{path[2:]}"
    return path


def parse_initial_date(initial_date):
    try:
        return datetime.strptime(initial_date, "%Y-%m-%d")
    except ValueError:
        print("Error: Initial date must be in YYYY-MM-DD format.", file=sys.stderr)
        sys.exit(1)


def format_git_date(commit_date):
    return commit_date.strftime("%Y-%m-%d 12:00:00 +0000")


def get_commit_hashes(num_commits):
    total_commits = int(
        run_command(["git", "rev-list", "--count", "HEAD"], capture_output=True)
    )
    commit_hashes = run_command(
        ["git", "rev-list", "HEAD", f"--max-count={num_commits}"],
        capture_output=True,
    ).splitlines()

    if len(commit_hashes) != num_commits:
        print(
            f"Error: Specified number of commits ({num_commits}) exceeds the current branch history.",
            file=sys.stderr,
        )
        sys.exit(1)

    commit_hashes.reverse()
    if num_commits == total_commits:
        revision_range = "HEAD"
    else:
        revision_range = f"{commit_hashes[0]}^..HEAD"

    return commit_hashes, revision_range


def build_env_filter_script(commit_date_map):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".sh", delete=False, newline="\n"
    ) as script_file:
        script_file.write("#!/bin/sh\n")
        script_file.write("# Map commit hashes to dates\n")

        for commit_hash, date in commit_date_map.items():
            script_file.write(f'if [ "$GIT_COMMIT" = "{commit_hash}" ]; then\n')
            script_file.write(f'    export GIT_AUTHOR_DATE="{date}"\n')
            script_file.write(f'    export GIT_COMMITTER_DATE="{date}"\n')
            script_file.write("fi\n")

        return script_file.name


def amend_commit_dates(initial_date, num_commits):
    current_date = parse_initial_date(initial_date)
    commit_hashes, revision_range = get_commit_hashes(num_commits)

    commit_date_map = {}
    for offset, commit_hash in enumerate(commit_hashes):
        formatted_date = format_git_date(current_date + timedelta(days=offset))
        commit_date_map[commit_hash] = formatted_date
        print(f"Will amend commit {commit_hash[:8]} with date: {formatted_date}")

    script_file_path = build_env_filter_script(commit_date_map)
    posix_script_path = windows_path_to_posix(script_file_path)

    try:
        print(f"\nRewriting commit history for the last {num_commits} commits...")

        env = os.environ.copy()
        env["FILTER_BRANCH_SQUELCH_WARNING"] = "1"
        env_filter = f". {shlex.quote(posix_script_path)}"

        run_command(
            [
                "git",
                "filter-branch",
                "-f",
                "--env-filter",
                env_filter,
                revision_range,
            ],
            env=env,
        )

        print("\nSuccessfully amended commit dates.")
        print(
            "Note: This has rewritten git history. If you've already pushed these commits,"
        )
        print("you'll need to force push: git push --force")
    finally:
        os.unlink(script_file_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            f"Usage: python {os.path.basename(sys.argv[0])} <initial-date:YYYY-MM-DD> <number-of-commits>",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        num_commits = int(sys.argv[2])
        if num_commits <= 0:
            raise ValueError
    except ValueError:
        print("Error: number-of-commits must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    amend_commit_dates(sys.argv[1], num_commits)
