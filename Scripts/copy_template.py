import argparse
import gitlab
import os
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser(description='Copy a template repository to new repositories')
parser.add_argument('--groups', help='Amount of groups to create')
parser.add_argument('--delete', help='If present, delete all projects in the target group', action='store_true')


args = parser.parse_args()

GITLAB_ACCESS_TOKEN = os.getenv('GITLAB_ACCESS_TOKEN')
GITLAB_URL = os.getenv('GITLAB_URL')
SOURCE_PROJECT_ID = os.getenv('SOURCE_PROJECT_ID')
TARGET_GROUP_ID = os.getenv('TARGET_GROUP_ID')
CI_CONFIG_PATH=os.getenv('CI_CONFIG_PATH')

print(f'Connecting to {GITLAB_URL} with access token {GITLAB_ACCESS_TOKEN}')
gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_ACCESS_TOKEN)

gl.auth()

# https://python-gitlab.readthedocs.io/en/stable/api/gitlab.html
# https://docs.gitlab.com/ee/api/issues.html#clone-an-issue
def clone_issue(from_project, to_project, issue):
    query = f'/projects/{from_project.id}/issues/{issue.iid}/clone'
    try:
        gl.http_post(query, query_data={
            'to_project_id': to_project.id,
            'with_notes': True
        })
    except gitlab.exceptions.GitlabCreateError as e:
        print(f'Failed to clone issue {issue.iid} from {from_project.name} to {to_project.name}: {e}')

def clone_project_to(group_id, project_name):
    project = gl.projects.get(SOURCE_PROJECT_ID)

    # Need to assign both username and access token to make it a 'valid' project url
    import_url = project.http_url_to_repo.replace('://', f'://{gl.user.username}:{GITLAB_ACCESS_TOKEN}@')

    # https://docs.gitlab.com/ee/api/projects.html#create-project
    cloned_project = gl.projects.create({
        'namespace_id': group_id,
        'name': project_name,
        'import_url': import_url,
        'initialize_with_readme': False,
        'ci_config_path': CI_CONFIG_PATH
        })

    # Only allow maintainers to push to the main branch
    # Allow developers to merge to the main branch
    cloned_project.protectedbranches.create(
        {
            'name': 'main',
            'merge_access_level': gitlab.const.AccessLevel.DEVELOPER,
            'push_access_level': gitlab.const.AccessLevel.MAINTAINER,
        }
    )

    for issue in project.issues.list(get_all=True):
        print(f'Cloning issue {issue.iid} from {project.name} to {cloned_project.name}')
        clone_issue(project, cloned_project, issue)

    print(f'Created project {cloned_project.name} with id {cloned_project.id} at {cloned_project.http_url_to_repo}')

if args.delete:
    target_group = gl.groups.get(TARGET_GROUP_ID)
    for project in target_group.projects.list(get_all=True):
        print(f'Deleting project {project.name} with id {project.id}')
        gl.projects.delete(project.id)

else:
    for i in range(int(args.groups)):
        clone_project_to(TARGET_GROUP_ID, "Group_" + str(i))
