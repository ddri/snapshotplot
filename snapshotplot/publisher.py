"""
Cloud publishing utilities for SnapshotPlot.

This module implements a simple publisher that sends snapshot metadata to a
cloud API (e.g., Supabase-backed), receives signed upload URLs, uploads files,
and finalizes the snapshot record.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import json
import mimetypes

import requests


@dataclass
class PublishConfig:
    cloud_url: str
    token: str
    project_id: str
    collection: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None
    commit_sha: Optional[str] = None
    branch: Optional[str] = None
    pr_number: Optional[int] = None


@dataclass
class SnapshotFiles:
    code_path: Path
    plot_path: Optional[Path]
    html_path: Optional[Path]


def discover_snapshot_files(snapshot_dir: Path) -> SnapshotFiles:
    code = None
    plot = None
    html = None

    for p in snapshot_dir.iterdir():
        if p.is_file():
            name = p.name
            if name.endswith("_code.py"):
                code = p
            elif name.endswith("_plot.png"):
                plot = p
            elif name.endswith("_snapshot.html"):
                html = p

    if code is None:
        raise FileNotFoundError("Could not find *_code.py in snapshot directory")

    return SnapshotFiles(code_path=code, plot_path=plot, html_path=html)


def _headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def request_signed_urls(config: PublishConfig, files: SnapshotFiles) -> Dict[str, str]:
    payload = {
        "project_id": config.project_id,
        "collection": config.collection,
        "title": config.title,
        "author": config.author,
        "description": config.description,
        "tags": config.tags,
        "repo_owner": config.repo_owner,
        "repo_name": config.repo_name,
        "commit_sha": config.commit_sha,
        "branch": config.branch,
        "pr_number": config.pr_number,
        "artifacts": {
            "plot": files.plot_path is not None,
            "code": True,
        },
    }
    url = f"{config.cloud_url.rstrip('/')}/api/snapshots/publish"
    resp = requests.post(url, headers=_headers(config.token), data=json.dumps(payload), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("upload_urls", {})


def upload_file_signed(url: str, file_path: Path) -> None:
    mime, _ = mimetypes.guess_type(str(file_path))
    mime = mime or "application/octet-stream"
    with open(file_path, "rb") as f:
        put = requests.put(url, data=f, headers={"Content-Type": mime}, timeout=120)
        put.raise_for_status()


def finalize_publish(config: PublishConfig, snapshot_id: Optional[str] = None) -> None:
    url = f"{config.cloud_url.rstrip('/')}/api/snapshots/finalize"
    payload = {"project_id": config.project_id, "snapshot_id": snapshot_id}
    try:
        resp = requests.post(url, headers=_headers(config.token), data=json.dumps(payload), timeout=30)
        # Accept 2xx or no-op if endpoint not present
        if resp.status_code >= 400:
            resp.raise_for_status()
    except requests.RequestException:
        # Non-fatal finalize
        pass


def publish_snapshot(snapshot_dir: str, config: PublishConfig) -> Dict[str, str]:
    """
    Publish a snapshot directory by requesting signed URLs and uploading files.

    Returns a dict with any returned URLs/IDs from the server response when available.
    """
    snap_path = Path(snapshot_dir)
    if not snap_path.exists() or not snap_path.is_dir():
        raise FileNotFoundError(f"Snapshot directory not found: {snapshot_dir}")

    files = discover_snapshot_files(snap_path)

    # Request signed URLs
    try:
        urls = request_signed_urls(config, files)
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to request signed URLs: {e}")

    # Upload code
    code_url = urls.get("code")
    if code_url:
        upload_file_signed(code_url, files.code_path)

    # Upload plot if present
    plot_url = urls.get("plot")
    if plot_url and files.plot_path is not None:
        upload_file_signed(plot_url, files.plot_path)

    finalize_publish(config, snapshot_id=urls.get("snapshot_id"))

    return urls 