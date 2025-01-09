import os
import shutil
import subprocess
from pathlib import Path
from fastapi.testclient import TestClient
from main import app, BASE_DIR

client = TestClient(app)

# Przygotowanie folderów testowych
TEST_REPO_DIR = BASE_DIR / "test-repo"
TEST_REPO_URL = "https://github.com/vilkh3m/tc_test.git"  # Zastąp swoim testowym repozytorium


def setup_module(module):
    """Przygotowanie środowiska testowego."""
    # Usuwanie poprzednich danych testowych
    if TEST_REPO_DIR.exists():
        shutil.rmtree(TEST_REPO_DIR)


def teardown_module(module):
    """Czyszczenie po zakończeniu testów."""
    if TEST_REPO_DIR.exists():
        shutil.rmtree(TEST_REPO_DIR)


def test_git_pull_clone():
    """Test klonowania repozytorium."""
    response = client.post(
        "/git-pull/",
        json={"repo_url": TEST_REPO_URL, "folder_name": "test-repo"}
    )
    assert response.status_code == 200
    assert "Repozytorium sklonowane pomyślnie" in response.json()["message"]
    assert TEST_REPO_DIR.exists()
    assert (TEST_REPO_DIR / ".git").exists()


def test_git_pull_update():
    """Test aktualizacji istniejącego repozytorium."""
    # Klonowanie repozytorium, jeśli jeszcze nie istnieje
    if not TEST_REPO_DIR.exists():
        subprocess.run(["git", "clone", TEST_REPO_URL, str(TEST_REPO_DIR)], check=True)

    # Testowanie `git pull`
    response = client.post(
        "/git-pull/",
        json={"repo_url": TEST_REPO_URL, "folder_name": "test-repo"}
    )
    assert response.status_code == 200
    assert "Git pull wykonano pomyślnie" in response.json()["message"]


def test_git_pull_invalid_repo():
    """Test obsługi błędnego URL repozytorium."""
    response = client.post(
        "/git-pull/",
        json={"repo_url": "https://invalid-url.git", "folder_name": "invalid-repo"}
    )
    assert response.status_code == 500
    assert "Błąd podczas klonowania repozytorium" in response.json()["detail"]


def test_count_branches():
    """Test liczenia gałęzi w repozytorium."""
    # Klonowanie repozytorium, jeśli jeszcze nie istnieje
    if not TEST_REPO_DIR.exists():
        subprocess.run(["git", "clone", TEST_REPO_URL, str(TEST_REPO_DIR)], check=True)

    # Testowanie liczenia gałęzi
    response = client.post(
        "/count-branches/",
        json={"folder_name": "test-repo"}
    )
    assert response.status_code == 200
    assert "Liczba gałęzi policzona pomyślnie" in response.json()["message"]
    assert response.json()["branch_count"] > 0
    assert isinstance(response.json()["branches"], list)


def test_count_branches_invalid_folder():
    """Test liczenia gałęzi w folderze, który nie jest repozytorium."""
    response = client.post(
        "/count-branches/",
        json={"folder_name": "nonexistent-folder"}
    )
    assert response.status_code == 400
    assert "Podany folder nie jest repozytorium Git." in response.json()["detail"]
