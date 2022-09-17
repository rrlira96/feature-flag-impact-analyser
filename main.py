from github import Github
import re

g = Github("<YOUR TOKEN HERE>")

regex_pattern = "(Add|added|adding)[a-zA-Z ]*(feature(-)?( )?(flag|toogle)?)"

with open("repos.txt", "r") as repos_file:
  for line in repos_file:
    repo_path = line.strip()
    repo = g.get_repo(repo_path)
    print("Repo -> ", repo.name)
    commits = repo.get_commits()
    for commit in commits:
        result = re.match(regex_pattern, commit.commit.message)
        if not result == None :
            print(commit.commit.message)
            check_runs = commit.get_check_runs()
            for check_run in check_runs:
                print(check_run.status)
                print(check_run.conclusion, "\n")





