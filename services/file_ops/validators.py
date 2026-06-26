ALLOWED_ROOTS=['root_1','root_2']

def validate_root(root:str)->bool:
    return root in ALLOWED_ROOTS
