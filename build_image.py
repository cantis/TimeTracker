# Description: This script is used to update the version in pyproject.toml and generate the requirements.txt file.
import os
import subprocess
import toml

# Generate the requirements.txt file, excluding dev dependencies
subprocess.run(['uv', 'pip', 'freeze', '>', 'requirements.txt'], shell=True)

# Update the version in pyproject.toml
with open('pyproject.toml') as f:
    data = toml.load(f)
    version = data['project']['version']
    version_parts = version.split('.')
    version_parts[-1] = str(int(version_parts[-1]) + 1)
    new_version = '.'.join(version_parts)
    os.environ['VERSION_TAG'] = new_version
    data['project']['version'] = new_version

with open('pyproject.toml', 'w') as f:
    toml.dump(data, f)

# Build the docker image
subprocess.run(['docker', 'compose', 'up', '--build', '-d'], check=True)

