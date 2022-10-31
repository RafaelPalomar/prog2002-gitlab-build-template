## Setting up runner
1. Build the image 'builder image' via the Dockerfile in `Docker/Dockerfile`
2. Reconfigure the shared runner
    1. You need to reconfigure the shared runner to run via docker and specify the newly built local image from step 1.
	2. Update the runner to be able to use the local image by adding `pull_policy = "if-not-present"` to /etc/gitlab-runner/config.toml
    3. Make sure to restart the runner using `gitlab-runner restart` after changing the settings
## Setting up the student repos
1. Add .gitlab-ci.yml to a repo accessible by the students
2. Run the `copy_template.py` script
    ``` bash
    python copy_template.py --access-token "" --gitlab-url "https://git.gvk.idi.ntnu.no" --ci-config-path ".gitlab-ci.yml@path-to-repo" --project-id 5 --target-group-id 20 --groups 3
    ```

Example ci config path for the old one in the build template: `.gitlab-ci.yml@course/prog2002/continuous-integration/buildtemplate` (change this path to the new one that will be hosting the ci config)

The other arguments are explained when running the script with `--help`

When you run the script it will clone and import from the repo/project specified project/repo into the specified group, and it will create as many clones as specified by `--groups`.

You should now be able to add a simple C++ program using `CMakeLists.txt` accompanied by a source file to the original/template repo you are cloning from. The CI should run when you push to a clone or create a merge requests in the clone.

It is worth noting that everything should work even if the only thing you have done for the new template repo is to create it and add the simple C++ program and then use it as the template. There is no need to configure anything else in the template repo.


**.env** file:
```
GITLAB_ACCESS_TOKEN = Gitlab access token
GITLAB_URL = Gitlab url
SOURCE_PROJECT_ID = Project id to clone from
TARGET_GROUP_ID = Group id to clone new project to
CI_CONFIG_PATH = Path to the CI config
```