import logging
import calendar
import time
from github import Github
import re
import csv

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

def check_api_rate_limit():
    logger.info('Checking API rate limit')
    remaining_limit = g.get_rate_limit().core.remaining
    if remaining_limit <= 200:
        core_rate_limit = g.get_rate_limit().core
        reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
        sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 5
        logger.info('The rate api limit is being reched. Sleeping {} seconds'.format(sleep_time))
        time.sleep(sleep_time)



g = Github("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")
#g = Github("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")

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

with open("repos.txt", "r") as repos_file:

    for line in repos_file:
        
        repo_path = line.strip()
        repo = g.get_repo(repo_path)
        logger.info("Repository: {}".format(repo.name))
        commits = repo.get_commits()        
        logger.info("Iterating {} commits".format(commits.totalCount))

        counterAdd = CiStatusCounter()
        counterRemove = CiStatusCounter()

        f_sha = open('sha_commit_'+ repo.name +'.csv', 'w')
        writer_sha = csv.writer(f_sha)
        header = ['commit_sha','add_or_remove']
        writer_sha.writerow(header)

        commit_count = 0
        for commit in commits:
            commit_count += 1
            match_add = re.search(
                add_ff_regex_pattern, commit.commit.message)
            match_remove = re.search(
                remove_ff_regex_pattern, commit.commit.message)
            
            is_merge_commit = True if 'Merge pull request' in commit.commit.message else False

            if not is_merge_commit and (match_add != None or match_remove != None):
                logger.info('================= commit {} of {} ================= sha {}'.format(commit_count, commits.totalCount, commit.sha))
                print(commit.commit.message)
                data_sha = [commit.sha, 'add' if match_add != None else 'remove']
                writer_sha.writerow(data_sha)

                if match_add != None:
                    counterAdd.ff_commits += 1
                    combined_status = commit.get_combined_status()
                    check_runs = commit.get_check_runs(status='completed')

                    has_external_ci_failed = verify_if_external_ci_failed(combined_status)
                    has_checks_failed = verify_if_checks_failed(check_runs)
                    
                    if has_external_ci_failed == None and has_checks_failed == None:
                        counterAdd.no_ci_commits += 1
                    elif has_external_ci_failed or has_checks_failed:
                        counterAdd.failed_ci_commits += 1
                    else:
                        counterAdd.not_failed_ci_commits += 1 
                else:
                    counterRemove.ff_commits += 1
                    combined_status = commit.get_combined_status()
                    check_runs = commit.get_check_runs(status='completed')

                    has_external_ci_failed = verify_if_external_ci_failed(combined_status)
                    has_checks_failed = verify_if_checks_failed(check_runs)
                    
                    if has_external_ci_failed == None and has_checks_failed == None:
                        counterRemove.no_ci_commits += 1
                    elif has_external_ci_failed or has_checks_failed:
                        counterRemove.failed_ci_commits += 1
                    else:
                        counterRemove.not_failed_ci_commits += 1
            if commit_count % 10000 == 0:
                check_api_rate_limit()

            

        data = [repo.full_name, repo.language, commits.totalCount, 'add', counterAdd.ff_commits,
                counterAdd.failed_ci_commits, counterAdd.not_failed_ci_commits, counterAdd.no_ci_commits,
                'remove', counterRemove.ff_commits, counterRemove.failed_ci_commits, counterRemove.not_failed_ci_commits,
                counterRemove.no_ci_commits]
        writer_ci.writerow(data)

        f_sha.close()

    f.close()
