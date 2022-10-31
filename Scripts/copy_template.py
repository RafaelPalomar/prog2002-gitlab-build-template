import argparse
import gitlab

parser = argparse.ArgumentParser(description='Copy a template repository to new repositories')
parser.add_argument('--access-token', help='Gitlab access token')
parser.add_argument('--gitlab-url', help='Gitlab url')
parser.add_argument('--project-id', help='Project id to copy from')
parser.add_argument('--target-group-id', help='Group id to copy create new projects in')
parser.add_argument('--groups', help='Amount of groups to create')
parser.add_argument('--delete', help='If present, delete all projects in the target group', action='store_true')
parser.add_argument('--ci-config-path', help='Path to the ci config')

args = parser.parse_args()

gl = gitlab.Gitlab(args.gitlab_url, private_token=args.access_token)

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
    project = gl.projects.get(args.project_id)

    # Need to assign both username and access token to make it a 'valid' project url
    import_url = project.http_url_to_repo.replace('://', f'://{gl.user.username}:{args.access_token}@')

    # https://docs.gitlab.com/ee/api/projects.html#create-project
    cloned_project = gl.projects.create({
        'namespace_id': group_id,
        'name': project_name,
        'import_url': import_url,
        'initialize_with_readme': False,
        'ci_config_path': args.ci_config_path
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
    target_group = gl.groups.get(args.target_group_id)
    for project in target_group.projects.list(get_all=True):
        print(f'Deleting project {project.name} with id {project.id}')
        gl.projects.delete(project.id)

else:
    for i in range(int(args.groups)):
        clone_project_to(args.target_group_id, "Group_" + str(i))
