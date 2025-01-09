import os
import shutil
import subprocess
from pathlib import Path
from fastapi.testclient import TestClient
from main import app, BASE_DIR

client = TestClient(app)

# Preparation of test folders
TEST_REPO_DIR = BASE_DIR / "test-repo"
TEST_REPO_URL = "https://github.com/vilkh3m/tc_test.git"  # Replace with your test repository


def setup_module(module):
    """Prepare the test environment."""
    # Remove previous test data
    if TEST_REPO_DIR.exists():
        shutil.rmtree(TEST_REPO_DIR)


def teardown_module(module):
    """Clean up after tests."""
    if TEST_REPO_DIR.exists():
        shutil.rmtree(TEST_REPO_DIR)


def test_git_pull_clone():
    """Test cloning a repository."""
    response = client.post(
        "/git-pull/",
        json={"repo_url": TEST_REPO_URL, "folder_name": "test-repo"}
    )
    assert response.status_code == 200
    assert "Repository cloned successfully" in response.json()["message"]
    assert TEST_REPO_DIR.exists()
    assert (TEST_REPO_DIR / ".git").exists()


def test_git_pull_update():
    """Test updating an existing repository."""
    # Clone the repository if it does not exist
    if not TEST_REPO_DIR.exists():
        subprocess.run(["git", "clone", TEST_REPO_URL, str(TEST_REPO_DIR)], check=True)

    # Test `git pull`
    response = client.post(
        "/git-pull/",
        json={"repo_url": TEST_REPO_URL, "folder_name": "test-repo"}
    )
    assert response.status_code == 200
    assert "Git pull executed successfully" in response.json()["message"]


def test_git_pull_invalid_repo():
    """Test handling of an invalid repository URL."""
    response = client.post(
        "/git-pull/",
        json={"repo_url": "https://invalid-url.git", "folder_name": "invalid-repo"}
    )
    assert response.status_code == 500
    assert "Error while cloning repository" in response.json()["detail"]


def test_count_branches():
    """Test counting branches in a repository."""
    # Clone the repository if it does not exist
    if not TEST_REPO_DIR.exists():
        subprocess.run(["git", "clone", TEST_REPO_URL, str(TEST_REPO_DIR)], check=True)

    # Test branch counting
    response = client.post(
        "/count-branches/",
        json={"folder_name": "test-repo"}
    )
    assert response.status_code == 200
    assert "Branch count calculated successfully" in response.json()["message"]
    assert response.json()["branch_count"] > 0
    assert isinstance(response.json()["branches"], list)


def test_count_branches_invalid_folder():
    """Test counting branches in a folder that is not a repository."""
    response = client.post(
        "/count-branches/",
        json={"folder_name": "nonexistent-folder"}
    )
    assert response.status_code == 400
    assert "The specified folder is not a Git repository." in response.json()["detail"]
