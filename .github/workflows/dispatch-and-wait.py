#!/usr/bin/env python3
"""Dispatch a GitHub Actions workflow in another Lyd Ark repository and wait for it."""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


API = "https://api.github.com"
POLL_SECONDS = 30
TIMEOUT_SECONDS = 5 * 60 * 60 + 50 * 60


def request(token, method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Lyd-Ark-build-orchestrator",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed ({error.code}): {detail}") from error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repository")
    parser.add_argument("--workflow", required=True, help="Workflow filename, e.g. build-payload.yml")
    parser.add_argument("--inputs", default="{}", help="JSON workflow_dispatch inputs")
    args = parser.parse_args()

    token = os.environ.get("ARK_WORKFLOW_TOKEN")
    if not token:
        raise SystemExit("ARK_WORKFLOW_TOKEN is not set. Add the repository secret before running this workflow.")

    inputs = json.loads(args.inputs)
    if not isinstance(inputs, dict):
        raise SystemExit("--inputs must be a JSON object")

    repo_path = f"/repos/{args.repo}"
    branch = request(token, "GET", repo_path + "/commits/main")
    expected_sha = branch["sha"]
    runs_path = repo_path + f"/actions/workflows/{args.workflow}/runs?event=workflow_dispatch&branch=main&per_page=20"
    previous_runs = request(token, "GET", runs_path)
    previous_ids = {item["id"] for item in previous_runs.get("workflow_runs", [])}

    print(f"Dispatching {args.repo}/{args.workflow} at main ({expected_sha})", flush=True)
    request(
        token,
        "POST",
        repo_path + f"/actions/workflows/{args.workflow}/dispatches",
        {"ref": "main", "inputs": inputs},
    )

    deadline = time.monotonic() + TIMEOUT_SECONDS
    run = None
    while time.monotonic() < deadline:
        listing = request(token, "GET", runs_path)
        candidates = [
            item for item in listing.get("workflow_runs", [])
            if item.get("head_sha") == expected_sha and item.get("id") not in previous_ids
        ]
        if candidates:
            run = max(candidates, key=lambda item: item.get("run_number", 0))
            break
        time.sleep(POLL_SECONDS)

    if run is None:
        raise SystemExit(f"Timed out waiting for the dispatched {args.workflow} run to appear.")

    run_id = run["id"]
    run_url = run.get("html_url", "")
    print(f"Started run {run_id}: {run_url}", flush=True)

    while time.monotonic() < deadline:
        state = request(token, "GET", repo_path + f"/actions/runs/{run_id}")
        status = state.get("status")
        conclusion = state.get("conclusion")
        if status == "completed":
            print(f"Completed {args.repo}/{args.workflow}: {conclusion} ({run_url})", flush=True)
            if conclusion != "success":
                raise SystemExit(f"Workflow failed with conclusion: {conclusion}")
            return
        print(f"Waiting for run {run_id}: {status}", flush=True)
        time.sleep(POLL_SECONDS)

    raise SystemExit(f"Timed out waiting for run {run_id}: {run_url}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
