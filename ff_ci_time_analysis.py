import calendar
import logging
from pydriller import Repository
from github import Github
from datetime import datetime
import re
import csv
import requests
import time


def processing_ci_time(repo, sha, add_or_remove):
    global sequence_of_commits_without_actions
    url = 'http://172.29.146.233:3000/repos/' + repo + '/actions/runs'
    params = {'head_sha': sha,'status':'success'}
    response = requests.get(url=url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['total_count'] != 0:
            workflow_runs = data['workflow_runs']
            total_time_in_sec = 0.0
            for run in workflow_runs:
                created_at = datetime.strptime(
                    run['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                updated_at = datetime.strptime(
                    run['updated_at'], '%Y-%m-%dT%H:%M:%SZ')

                run_timing = (updated_at - created_at).total_seconds()
                total_time_in_sec += run_timing

            is_feature_flag = True if add_or_remove != None else False
            data = [repo, sha, total_time_in_sec, is_feature_flag,
                    add_or_remove if add_or_remove != None else 'N/A']
            writer_time.writerow(data)
            sequence_of_commits_without_actions = 0
        else:
            sequence_of_commits_without_actions += 1
    else:
        logger.error('ERROR sha {} : {}'.format(sha, response))


def processing_commit(sha, msg):
    logger.info('========= commit {} ========= sha {} ========='.format(commit_count, sha))
    match_add = re.search(
        add_ff_regex_pattern, msg)
    match_remove = re.search(
        remove_ff_regex_pattern, msg)

    if match_add != None or match_remove != None:  

        if match_add != None:
            processing_ci_time(repo.full_name, sha, 'add')
        else:
            processing_ci_time(repo.full_name, sha, 'remove')
    else:
        processing_ci_time(repo.full_name, sha, None)

def check_api_rate_limit():
    logger.info('Checking API rate limit')
    remaining_limit = g_2.get_rate_limit().core.remaining
    if remaining_limit <= 120:
        core_rate_limit = g_2.get_rate_limit().core
        reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
        sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 5
        logger.info('The rate api limit is being reched. Sleeping {} seconds'.format(sleep_time))
        time.sleep(sleep_time)



g = Github(base_url="http://172.29.146.233:3000")
g_2 = Github('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')

add_ff_regex_pattern = "(?i)(add|added|adding)[\s\S]*(feature(-)?( )?(flag|toggle|flipper|switch))"
remove_ff_regex_pattern = "(?i)(remove|removing|removed|delete|deleting|deleted)[\s\S]*(feature(-)?( )?(flag|toggle|flipper|switch))"
#timestr = time.strftime("%Y%m%d-%H%M%S")
sequence_of_commits_without_actions = 0

logger = logging.getLogger()
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.basicConfig(filename="log_error.log",
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.ERROR,
    datefmt='%Y-%m-%d %H:%M:%S')


with open("repos_time.txt", "r") as repos_file:
    for line in repos_file:
        start_time = time.time()
        repo_path = line.strip()
        repo = g.get_repo(repo_path)
        logger.info("Repository: {}".format(repo.name))

        f_time = open('ci_time_' + repo.name + '.csv', 'w')
        writer_time = csv.writer(f_time)
        header = ['repository', 'commit_sha', 'ci_time',
                  'is_feature_flag', 'ff_add_or_remove', ]
        writer_time.writerow(header)

        repo_url = 'https://github.com/' + repo_path

        commit_count = 0
        for commit in Repository(repo_url, order='reverse').traverse_commits():
            commit_count += 1
            processing_commit(commit.hash, commit.msg)
            if commit_count % 100 == 0:
                check_api_rate_limit()
            if sequence_of_commits_without_actions > 200:
                logger.info('Sequence of 200+ commits without actions found, breaking loop')
                break

        
        f_time.close()
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info('Execution time: {} seconds'.format(elapsed_time))
