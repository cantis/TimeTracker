April 2025

Evan's time tracking application - a Python learning project. 

See Docs folder for more documentation and how to set up the .env file

To build the docker image: 
```powershell
# Bump patch version and build
PS> py build_image.py

# Or build with current version (no version bump)
PS> py build_current.py
```

Note: `build_image.py` will:
1. Update requirements.txt from current environment
2. Bump the patch version in `pyproject.toml`
3. Build and tag the Docker image with the new version (e.g., `time-tracker:0.1.36`)
4. Start the container with the new image

The `build_current.py` script builds without bumping the version.

To run the docker image:
```powershell
PS> docker compose up -d
```



