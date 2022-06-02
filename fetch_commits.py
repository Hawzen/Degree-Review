import sqlite3

from github import Github
from pandas import to_datetime

with open(".env") as file:
    env = {e.split("=")[0]: e.split("=")[1] for e in file.read().split("\n") if e}

db = sqlite3.connect("db.sqlite3")
g = Github(env["github_access_token"])

cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS commits(
        repo TEXT not NULL,
        date DATE not NULL,
        rawData TEXT not NULL
    )
""")
db.commit()

for repo in g.get_user().get_repos():
    cursor = db.cursor()
    records = [
        (repo.name, str(to_datetime(commit.raw_data["commit"]["committer"]["date"])), str(commit.raw_data)) 
            for commit in repo.get_commits() if commit.raw_data["commit"]["committer"]["name"] == env["github_username"]
            ]
    cursor.executemany("""
            INSERT INTO commits(repo, date, rawData)
            values(?, ?, ?)
        """, (records))
    db.commit()