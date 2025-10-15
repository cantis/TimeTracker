April 2025

Evan's time tracking application - a Python learning project. 

See Docs folder for more documentation and how to set up the .env file

To build the docker image: 
```powershell
PS> py build_image.py
```

Note: Build_image.py will update the version number of the application in `pyproject.toml` and that version number is used in the docker image tag.

To run the docker image:
```powershell
PS> docker compose up -d
```



