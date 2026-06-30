ALLOWED_COMMANDS = {
    'import_app': ['python', '-c', "import app; print('APP_IMPORT_OK')"],
    'compileall': ['python', '-m', 'compileall', '.'], 
}


def get_command(name: str):
    return ALLOWED_COMMANDS.get(name)


def list_allowed():
    return sorted(ALLOWED_COMMANDS.keys())
