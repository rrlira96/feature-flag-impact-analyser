from github import Github, UnknownObjectException
import csv
import sys

g = Github(login_or_token=sys.argv[1])

f_ci = open('repos_with_ci.csv', 'w')
writer_ci = csv.writer(f_ci)
header = ['repository']
writer_ci.writerow(header)

f_actions = open('repos_with_actions.csv', 'w')
writer_actions = csv.writer(f_actions)
writer_actions.writerow(header)


def check_if_has_ci(commits):
    has_external_ci = False
    has_checks = False
    for commit in commits:
        status_count = commit.get_combined_status().total_count
        if status_count != 0:
            has_external_ci = True
        check_runs = commit.get_check_runs()
        if check_runs.totalCount != 0:
            has_checks = True

    print('Repo: {} , has_external_ci: {} , has_checks: {}'.format(repo_path, has_external_ci, has_checks))
    return True if has_external_ci or has_checks else False


def check_if_has_actions():
    workflows_runs_count = repo.get_workflow_runs().totalCount
    print('Repo: {}, workflows_runs_count: {}'.format(repo_path, workflows_runs_count))
    return True if workflows_runs_count != 0 else False


with open("input_repos.txt", "r") as repos:

    for line in repos:
        repo_path = line.strip()
        try:
            repo = g.get_repo(repo_path)
    
            commits = repo.get_commits().get_page(0)
            has_ci = check_if_has_ci(commits)

            has_actions = check_if_has_actions()

            if has_ci:
                data = [repo.full_name]
                writer_ci.writerow(data)

            if has_actions:
                data = [repo.full_name]
                writer_actions.writerow(data)

        except UnknownObjectException as ex:
            print("Repository {} was not found".format(repo_path))
        except Exception as ex:
            print('Repo {} failed: {}'.format(repo_path, ex))

f_ci.close()
f_actions.close()