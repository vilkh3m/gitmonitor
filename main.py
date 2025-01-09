from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import subprocess

app = FastAPI()

# Parent folder for repositories
BASE_DIR = Path("./app/gitmonitor")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Input data model
class GitPullRequest(BaseModel):
    repo_url: str
    folder_name: str

class BranchCountRequest(BaseModel):
    folder_name: str

@app.post("/git-pull/")
async def git_pull(request: GitPullRequest):
    """
    Clones a Git repository or performs `git pull` if the repository already exists.
    """
    repo_url = request.repo_url
    folder_name = request.folder_name

    repo_path = BASE_DIR / folder_name

    # If the folder does not exist, clone the repository
    if not repo_path.exists():
        try:
            result = subprocess.run(
                ["git", "clone", repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                check=True
            )
            return {"message": "Repository cloned successfully", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Error while cloning repository: {e.stderr}")

    # If the folder exists, perform `git pull`
    if (repo_path / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "pull"],
                capture_output=True,
                text=True,
                check=True
            )
            return {"message": "Git pull executed successfully", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Error while performing git pull: {e.stderr}")
    else:
        raise HTTPException(status_code=400, detail="The specified folder exists but is not a Git repository.")

@app.post("/count-branches/")
async def count_branches(request: BranchCountRequest):
    """
    Counts the number of branches in the specified Git repository.
    """
    folder_name = request.folder_name
    repo_path = BASE_DIR / folder_name

    # Check if the folder exists and is a Git repository
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="The specified folder is not a Git repository.")

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "branch", "-r"],
            capture_output=True,
            text=True,
            check=True
        )
        branches = result.stdout.strip().split("\n")
        branch_count = len(branches)
        return {
            "message": "Branch count calculated successfully",
            "branch_count": branch_count,
            "branches": branches
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error while counting branches: {e.stderr}")
