# Description: Build Docker image with current version (without bumping)
import os
import subprocess

import toml

# Read the current version from pyproject.toml
with open('pyproject.toml', 'r') as f:
    pyproject = toml.load(f)
    version = pyproject['project']['version']

print(f'Building Docker image with current version: {version}')

# Set VERSION_TAG environment variable and build the docker image
env = os.environ.copy()
env['VERSION_TAG'] = version
subprocess.run(['docker', 'compose', 'build'], env=env, check=True)

print(f'\nBuild complete! Image tagged as: time-tracker:{version}')
print('To start the container, run: docker compose up -d')
