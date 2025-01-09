from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import subprocess

app = FastAPI()

# Nadrzędny folder na repozytoria
BASE_DIR = Path("/app/gitmonitor")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Model danych wejściowych
class GitPullRequest(BaseModel):
    repo_url: str
    folder_name: str

class BranchCountRequest(BaseModel):
    folder_name: str

@app.post("/git-pull/")
async def git_pull(request: GitPullRequest):
    """
    Klonuje repozytorium Git lub wykonuje `git pull`, jeśli repozytorium już istnieje.
    """
    repo_url = request.repo_url
    folder_name = request.folder_name

    repo_path = BASE_DIR / folder_name

    # Jeśli folder nie istnieje, klonuj repozytorium
    if not repo_path.exists():
        try:
            result = subprocess.run(
                ["git", "clone", repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                check=True
            )
            return {"message": "Repozytorium sklonowane pomyślnie", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Błąd podczas klonowania repozytorium: {e.stderr}")

    # Jeśli folder istnieje, wykonaj `git pull`
    if (repo_path / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "pull"],
                capture_output=True,
                text=True,
                check=True
            )
            return {"message": "Git pull wykonano pomyślnie", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Błąd podczas wykonywania git pull: {e.stderr}")
    else:
        raise HTTPException(status_code=400, detail="Podany folder istnieje, ale nie jest repozytorium Git.")

@app.post("/count-branches/")
async def count_branches(request: BranchCountRequest):
    """
    Liczy liczbę gałęzi w podanym repozytorium Git.
    """
    folder_name = request.folder_name
    repo_path = BASE_DIR / folder_name

    # Sprawdzenie, czy folder istnieje i jest repozytorium Git
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="Podany folder nie jest repozytorium Git.")

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "branch", "-r"],
            capture_output=True,
            text=True,
            check=True
        )
        branches = result.stdout.strip().split("\n")
        branch_count = len(branches)
        return {"message": "Liczba gałęzi policzona pomyślnie", "branch_count": branch_count, "branches": branches}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas liczenia gałęzi: {e.stderr}")
