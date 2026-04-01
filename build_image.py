# Description: This script is used to update the version in pyproject.toml and generate the requirements.txt file.
import os
import subprocess

import toml

# Generate the requirements.txt file, excluding dev dependencies
subprocess.run(['uv', 'pip', 'freeze', '>', 'requirements.txt'], shell=True)

# Update the version in pyproject.toml
subprocess.run(['uv', 'version', '--bump', 'patch'])

# Read the updated version from pyproject.toml
with open('pyproject.toml', 'r') as f:
    pyproject = toml.load(f)
    version = pyproject['project']['version']

print(f'Building Docker image with version: {version}')

# Set VERSION_TAG environment variable and build the docker image
env = os.environ.copy()
env['VERSION_TAG'] = version
subprocess.run(['docker', 'compose', 'up', '--build', '-d'], env=env, check=True)
