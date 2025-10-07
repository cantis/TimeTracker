# Description: This script is used to update the version in pyproject.toml and generate the requirements.txt file.
import subprocess

# Generate the requirements.txt file, excluding dev dependencies
subprocess.run(['uv', 'pip', 'freeze', '>', 'requirements.txt'], shell=True)

# Update the version in pyproject.toml
subprocess.run(['uv', 'version', '--bump', 'patch'])

# Build the docker image
subprocess.run(['docker', 'compose', 'up', '--build', '-d'], check=True)
