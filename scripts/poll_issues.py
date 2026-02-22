#!/usr/bin/env python3
"""
GitHub Issue Polling Script

Polls GitHub for new open issues every 30 minutes and processes them.

Usage:
    python scripts/poll_issues.py

Or set up a cron job:
    */30 * * * * /path/to/venv/bin/python /path/to/metis/scripts/poll_issues.py
"""
import os
import sys
import time
import urllib.request
import json
import subprocess
from pathlib import Path

# Configuration
REPO_OWNER = "redjump-ai"
REPO_NAME = "metis"
POLL_INTERVAL = 1800  # 30 minutes in seconds


def get_github_api_url():
    return f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"


def get_open_issues():
    """Fetch open issues from GitHub API."""
    url = get_github_api_url()
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    
    # Add GitHub token if available
    token = os.getenv("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            # Filter only open issues (not PRs)
            return [issue for issue in data if not issue.get("pull_request")]
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return []


def get_local_issue_numbers():
    """Get issue numbers that have been processed locally."""
    # You could track processed issues in a file
    processed_file = Path(__file__).parent / ".processed_issues"
    if processed_file.exists():
        with open(processed_file) as f:
            return set(int(line.strip()) for line in f if line.strip())
    return set()


def mark_issue_processed(issue_number):
    """Mark an issue as processed."""
    processed_file = Path(__file__).parent / ".processed_issues"
    with open(processed_file, "a") as f:
        f.write(f"{issue_number}\n")


def notify_new_issues(issues):
    """Notify about new issues (print to stdout)."""
    if not issues:
        return
    
    print(f"\n{'='*50}")
    print(f"Found {len(issues)} new open issue(s):")
    print(f"{'='*50}")
    for issue in issues:
        print(f"  #{issue['number']}: {issue['title']}")
        print(f"     URL: {issue['html_url']}")
    print(f"{'='*50}\n")


def main():
    print(f"GitHub Issue Poller started for {REPO_OWNER}/{REPO_NAME}")
    print(f"Poll interval: {POLL_INTERVAL} seconds (30 minutes)")
    print("Press Ctrl+C to stop\n")
    
    processed_issues = get_local_issue_numbers()
    
    while True:
        try:
            issues = get_open_issues()
            new_issues = [i for i in issues if i["number"] not in processed_issues]
            
            if new_issues:
                notify_new_issues(new_issues)
                
                # Process each new issue
                for issue in new_issues:
                    print(f"Processing issue #{issue['number']}: {issue['title']}")
                    # TODO: Add your issue processing logic here
                    # For example, you could clone the repo, run a script, etc.
                    mark_issue_processed(issue["number"])
                    processed_issues.add(issue["number"])
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No new issues found")
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nPolling stopped.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
