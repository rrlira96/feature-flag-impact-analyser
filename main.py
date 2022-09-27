from github import Github
import re
import csv

g = Github("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")

add_ff_regex_pattern = "(?i)(add|added|adding)[a-zA-Z ]*(feature(-)?( )?(flag|toggle|flipper|switch))"
remove_ff_regex_pattern = "(?i)(remove|removing|removed|delete|deleting|deleted)[a-zA-Z ]*(feature(-)?( )?(flag|toggle|flipper|switch))"

f = open('output.csv', 'w')
writer = csv.writer(f)
header = ['REPOSITORY', 'FF COMMITS', 'SUCCESSFUL', 'FAILED/ERROR', 'PENDING']
writer.writerow(header)

with open("repos.txt", "r") as repos_file:

    for line in repos_file:
        repo_path = line.strip()
        repo = g.get_repo(repo_path)
        print("Repository:", repo.name)
        commits = repo.get_commits()
        commits_adding_ff = 0
        successful_commits = 0
        failed_commits = 0
        pending_commits = 0
        print("Iterating {} commits".format(commits.totalCount))
        for commit in commits:
            adding_match = re.match(
                add_ff_regex_pattern, commit.commit.message)
            if not adding_match == None:
                commits_adding_ff += 1
                print(commit.commit.message)
                print("SHA:", commit.sha)
                print("commit_status:", commit.get_combined_status().state)
                commit_state = commit.get_combined_status().state
                if commit_state == 'success':
                    successful_commits += 1
                elif commit_state == 'pending':
                    pending_commits += 1
                else:
                    failed_commits += 1

        print("FF_COMMITS: {} -------- SUCCESSFUL: {} -------- FAILED/ERROR: {} -------- PENDING: {}".format(
            commits_adding_ff, successful_commits, failed_commits, pending_commits))

        data = [repo_path, commits_adding_ff,
                successful_commits, failed_commits, pending_commits]
        writer.writerow(data)

f.close()
