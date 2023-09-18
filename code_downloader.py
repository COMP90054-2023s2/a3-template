from re import L
import sys
import os
import importlib
import traceback
import datetime
import time
import pickle
import random
import git
import shutil
import logging
import pytz
import json

from optparse import OptionParser









GIT_TOKEN_PATH = "configs/git_token.txt"
TIMEZONE = pytz.timezone('Australia/Melbourne')
DATE_FORMAT = '%d/%m/%Y %H:%M:%S'  # RMIT Uni (Australia)

# CLASS DEF ----------------------------------------------------------------------------------------------------------#

def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.InvalidGitRepositoryError:
        return False

# Extract the timestamp for a given tag in a repo
def get_commit_time(repo:git.Repo):
    """
    Returns the commit time based on the TIMEZONE

    :param repo: the repository 
    :return: the commit time
    """
    commit = repo.commit()
    commit_date = datetime.datetime.fromtimestamp(commit.committed_date, tz=TIMEZONE)
    return commit_date.strftime(DATE_FORMAT)



def gitCloneTeam(team_name,agent_url,agent_commit_id, output_path):
    
    token = None
    with open(GIT_TOKEN_PATH, "r") as f:
        token = f.read()
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)    

    clone_url = f"https://{token}@{agent_url.replace('https://','')}"

    commit_id = agent_commit_id
    # branch = "master"
    git_status = False
    file_status = False
    # submission_time='N/A'
    # if not os.path.exists(repo_path):
    #     os.makedirs(repo_path)

    if not is_git_repo(output_path):
        # logging.info(f'Trying to clone NEW team repo from URL {clone_url}.')
        try:
            repo = git.Repo.clone_from(clone_url, output_path,  no_checkout=True)
            repo.git.checkout(commit_id)
            git_status = True
            # repo = git.Repo.clone_from(clone_url, repo_path)
            # submission_time = get_commit_time(repo)
            # logging.info(f'Team {team_name} cloned successfully with tag date {submission_time}.')
            # team_info.update({'git':'succ'})
            # team_info.update({'comments':'N/A'})
            # team_info.update({'submitted_time': submission_time})
            repo.close()
            # teams_new.append(team_name)
        except git.GitCommandError as e:
            traceback.print_exc()
            pass
            # teams_missing.append(team_name)
            # logging.warning(f'Repo for team {team_name} with tag/branch "{branch}" cannot be cloned: {e.stderr.replace(token,"")}')

            # team_info.update({'git':'failed'})
            # team_info.update({'comments':f'Repo for team {team_name} with tag/branch {branch} cannot be cloned: {e.stderr.replace(token,"")}'})
            # repo.close()
        except KeyboardInterrupt:
            
            logging.warning('Script terminated via Keyboard Interrupt; finishing...')
            sys.exit("keyboard interrupted!")
            # repo.close()
        except TypeError as e:
            traceback.print_exc()
            # logging.warning(f'Repo for team {team_name} was cloned but has no tag {branch}, removing it...: {e}')
            shutil.rmtree(output_path)
            # teams_notag.append(team_name)
            # team_info.update({'git':'failed'})
            # team_info.update({'comments':f'Repo for team {team_name} was cloned but has no tag {branch}, removing it...: {e}'})
            # repo.close()
        except Exception as e:
            traceback.print_exc()
            pass
            # logging.error(
            #     f'Repo for team {team_name} cloned but unknown error when getting tag {branch}; should not happen. Stopping... {e}')
            # team_info.update({'git':'failed'})
            # team_info.update({'comments':f'Repo for team {team_name} cloned but unknown error when getting tag {branch}; should not happen. Stopping... {e}'})
            # # repo.close()  
    else:
        # team_info.update({'git':'succ'})
        pass
    print(git_status)
    if git_status:
        try:

            # shutil.copy2(f"{output_path}/search.py", 'search.py')
            # shutil.copy2(f"{output_path}/searchAgents.py", 'searchAgents.py')
            if not os.path.exists(f"agents/{team_name}"):
                shutil.copytree(f"{output_path}/agents/{team_name}", f"agents/{team_name}")
            if os.path.exists(f"agents/{team_name}/myTeam.py"):
                file_status = True
        except:
            traceback.print_exc()
        shutil.rmtree(f"{output_path}")

    return git_status,file_status


def loadParameter():

    """
    Processes the command used to run Yinsh from the command line.
    """
    usageStr = """
    USAGE:      python runner.py <options>
    EXAMPLES:   (1) python runner.py
                    - starts a game with four random agents.
                (2) python runner.py -c MyAgent
                    - starts a fully automated game where Citrine team is a custom agent and the rest are random.
    """
    parser = OptionParser(usageStr)
    # parser.add_option('-r','--red', help='Red team agent file', default=DEFAULT_AGENT)
    # parser.add_option('-b','--blue', help='Blue team agent file', default=DEFAULT_AGENT) 
    # parser.add_option('-a','--agents', help='A list of the agents, etc, agents.myteam.player', default="agents.generic.random,agents.generic.random") 

    # parser.add_option('--redName', help='Red agent name', default='Red')
    # parser.add_option('--blueName', help='Blue agent name', default='Blue') 


    # whether load team from cloud
    # parser.add_option('--cloud', action='store_true', help='Display output as text only (default: False)', default=False)

    # parser.add_option('--redURL', help='Red team repo URL', default=None) 
    # parser.add_option('--redCommit', help='Red team commit id', default=None) 
    # parser.add_option('--blueURL', help='Blue team repo URL', default=None) 
    # parser.add_option('--blueCommit', help='Blue team commit id', default=None) 

    parser.add_option('--agent_url', help='url', default="")
    parser.add_option('--agent_commit_id', help='commit id', default="") 
    parser.add_option('--team_name', help='team_name', default="") 
    parser.add_option('--id',type="int",default=0)
    
    options, otherjunk = parser.parse_args(sys.argv[1:] )
    assert len(otherjunk) == 0, "Unrecognized options: " + str(otherjunk)

    return options

# MAIN ---------------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':

    """
    The main function called when advance_model.py is run
    from the command line:

    > python runner.py

    See the usage string for more details.

    > python runner.py --help
    """
    msg = ""
    options = loadParameter()
    team_name = options.team_name
    agent_url = options.agent_url
    agent_commit_id = options.agent_commit_id
    # matches = dict()
    # 
    
    with open("output/matches.json","r") as f:
        matches = json.load(f)
    # if not "teams" in matches.keys():
    #     matches['teams'] = dict()
    
    # team = {
    #     "team_name": options.team_name,
    #     "commit_id": options.agent_commit_id,
    #     "git_status": 
    # }
    
    
    git_status,file_status = gitCloneTeam(team_name,agent_url,agent_commit_id, "temp")
    team = {
        "team_name": team_name,
        "commit_id": agent_commit_id,
        "git_status": git_status,
        "file_status": file_status
        
    }
    if 'teams' not in matches.keys():
        matches['teams'] = dict()
    print(options.id)
    matches['teams'][options.id]= team
    with open("output/matches.json","w") as f:
        json.dump(matches,f)