'''Debug script to check environment variables in Docker container.'''

import os
from pathlib import Path

from dotenv import load_dotenv

# Try to load .env file if exists
load_dotenv()

def debug_environment() -> None:
    '''Print environment information for debugging.'''
    print('=== Environment Variables ===')
    for key, value in sorted(os.environ.items()):
        print(f'{key}={value}')  
    
    print('\n=== Important Paths ===')
    app_dir = Path('/app')
    print(f'App directory: {app_dir} (exists: {app_dir.exists()})')
    data_dir = Path('/app/data')
    print(f'Data directory: {data_dir} (exists: {data_dir.exists()}, writable: {os.access(str(data_dir), os.W_OK)})')
    instance_dir = Path('/app/instance')
    print(f'Instance directory: {instance_dir} (exists: {instance_dir.exists()}, writable: {os.access(str(instance_dir), os.W_OK)})')
    
    print('\n=== Directory Contents ===')
    for directory in ['/app', '/app/data', '/app/instance']:
        path = Path(directory)
        print(f'{directory} contents:')
        if path.exists():
            for item in path.iterdir():
                print(f" - {item} ({'dir' if item.is_dir() else 'file'})")
        else:
            print(' * Directory doesn`t exist!')
    
    print('\n=== Database Path Check ===')
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI', 'Not set')
    print(f'Database URI: {db_uri}')
    
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        full_path = Path('/' if db_path.startswith('/') else '') / db_path
        print(f'Database path: {full_path}')
        print(f'DB parent exists: {full_path.parent.exists()}')
        if full_path.parent.exists():
            print(f'DB parent is writable: {os.access(str(full_path.parent), os.W_OK)}')
            print(f'DB exists: {full_path.exists()}')
            if not full_path.exists():
                try:
                    # Try to create an empty file to test write access
                    with open(full_path, 'a'):
                        pass
                    print('Successfully created test database file')
                except Exception as e:
                    print(f'Error creating test file: {e}')
        print('Parent directory contents:')
        if full_path.parent.exists():
            for item in full_path.parent.iterdir():
                print(f' - {item}')

if __name__ == '__main__':
    debug_environment()