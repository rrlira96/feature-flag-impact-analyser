import logging
import calendar
import time
from pydriller import Repository
from github import Github, Commit
import re
import csv
import sys

class CiStatusCounter:
    def __init__(self):
        self.ff_commits = 0
        self.failed_ci_commits = 0
        self.not_failed_ci_commits = 0
        self.no_ci_commits = 0

def verify_if_external_ci_failed(combined_status):
    if combined_status.total_count != 0:
        if combined_status.state == 'failure':
            return True
        else: 
            return False
    else:
        return None    

def verify_if_checks_failed(check_runs):
    if check_runs.totalCount != 0:
        for check_run in check_runs:
            if check_run.conclusion == 'failure':
                return True
        return False
    return None

def processing_ci_status(ciCounter: CiStatusCounter, commit: Commit):
    ciCounter.ff_commits += 1
    combined_status = commit.get_combined_status()
    check_runs = commit.get_check_runs(status='completed')
    has_external_ci_failed = verify_if_external_ci_failed(combined_status)
    has_checks_failed = verify_if_checks_failed(check_runs)
            
    if has_external_ci_failed == None and has_checks_failed == None:
        ciCounter.no_ci_commits += 1
    elif has_external_ci_failed or has_checks_failed:
        ciCounter.failed_ci_commits += 1
    else:
        ciCounter.not_failed_ci_commits += 1 


def processing_commit(commit_sha, commit_message):
    match_add = re.search(
        add_ff_regex_pattern, commit_message)
    match_remove = re.search(
        remove_ff_regex_pattern, commit_message)
    
    if match_add != None or match_remove != None:
        logger.info('================= commit {} of {} ================='.format(commit_count, commits_total_count))
        data_sha = [commit_sha, 'add' if match_add != None else 'remove']
        writer_sha.writerow(data_sha)

        commit = repo.get_commit(commit_sha)

        if match_add != None:
            processing_ci_status(counterAdd, commit)
        else:
            processing_ci_status(counterRemove, commit)

def check_api_rate_limit():
    logger.info('Checking API rate limit')
    remaining_limit = g.get_rate_limit().core.remaining
    if remaining_limit <= 200:
        core_rate_limit = g.get_rate_limit().core
        reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
        sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 5
        logger.info('The rate api limit is being reched. Sleeping {} seconds'.format(sleep_time))
        time.sleep(sleep_time)

g = Github(login_or_token=sys.argv[1])

add_ff_regex_pattern = "(?i)(add|added|adding)[\s\S]*(feature(-)?( )?(flag|toggle|flipper|switch))"
remove_ff_regex_pattern = "(?i)(remove|removing|removed|delete|deleting|deleted)[\s\S]*(feature(-)?( )?(flag|toggle|flipper|switch))"

f = open('ci_status.csv', 'a')
writer_ci = csv.writer(f)
#header = ['repository', 'language', 'total_commits', 'add_or_remove', 'feature_flag_commits', 'failed_ci_commits', 'not_failed_ci_commits', 'no_ci_commits',
#          'add_or_remove', 'feature_flag_commits', 'failed_ci_commits', 'not_failed_ci_commits', 'no_ci_commits']
#writer_ci.writerow(header)

logger = logging.getLogger()
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.basicConfig(filename="log_error.log",
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.ERROR,
    datefmt='%Y-%m-%d %H:%M:%S')

with open("repos.txt", "r") as repos_file:

    for line in repos_file:
        start_time = time.time()
        repo_path = line.strip()
        repo = g.get_repo(repo_path)
        logger.info("Repository: {}".format(repo.name))
        commits_total_count = repo.get_commits().totalCount        
        logger.info("Iterating {} commits".format(commits_total_count))

        counterAdd = CiStatusCounter()
        counterRemove = CiStatusCounter()

        f_sha = open('sha_commit_'+ repo.name +'.csv', 'w')
        writer_sha = csv.writer(f_sha)
        header = ['commit_sha','add_or_remove']
        writer_sha.writerow(header)

        repo_url = 'https://github.com/' + repo_path

        commit_count = 0
        for commit in Repository(repo_url).traverse_commits():
            commit_count += 1
            processing_commit(commit.hash, commit.msg)
            if commit_count % 10000 == 0:
                check_api_rate_limit()


        data = [repo.full_name, repo.language, commits_total_count, 'add', counterAdd.ff_commits,
                counterAdd.failed_ci_commits, counterAdd.not_failed_ci_commits, counterAdd.no_ci_commits,
                'remove', counterRemove.ff_commits, counterRemove.failed_ci_commits, counterRemove.not_failed_ci_commits,
                counterRemove.no_ci_commits]
        writer_ci.writerow(data)

        f_sha.close()
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info('Execution time: {} seconds'.format(elapsed_time))


    f.close()
