import argparse
import gitlab

parser = argparse.ArgumentParser(description='Copy a template repository to new repositories')
parser.add_argument('--access-token', help='Gitlab access token')
parser.add_argument('--gitlab-url', help='Gitlab url')
parser.add_argument('--project-id', help='Project id to copy from')
parser.add_argument('--target-group-id', help='Group id to copy create new projects in')
parser.add_argument('--groups', help='Amount of groups to create')
parser.add_argument('--delete', help='If present, delete all projects in the target group', action='store_true')

ci_config_path = '.gitlab-ci.yml@gitlab-instance-4ba8498b/gitlab-ci-test'

args = parser.parse_args()

gl = gitlab.Gitlab(args.gitlab_url, private_token=args.access_token)

gl.auth()

def clone_project_to(group_id, project_name):
    project = gl.projects.get(args.project_id)

    # Need to assign both username and access token to make it a 'valid' project url
    import_url = project.http_url_to_repo.replace('://', f'://{gl.user.username}:{args.access_token}@')

    cloned_project = gl.projects.create({
        'namespace_id': group_id,
        'name': project_name,
        'import_url': import_url,
        'initialize_with_readme': False
        })
    print(f'Created project {cloned_project.name} with id {cloned_project.id} at {cloned_project.http_url_to_repo}')

if args.delete:
    target_group = gl.groups.get(args.target_group_id)
    for project in target_group.projects.list(get_all=True):
        print(f'Deleting project {project.name} with id {project.id}')
        gl.projects.delete(project.id)

else:
    for i in range(int(args.groups)):
        clone_project_to(args.target_group_id, "Group_" + str(i))
