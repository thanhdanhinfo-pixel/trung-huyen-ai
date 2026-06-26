from .validators import validate_root
from .audit import record

def dry_run(src_root,dst_root,item_id):
    ok=validate_root(src_root) and validate_root(dst_root)
    return record('copy',{'allowed':ok,'item_id':item_id,'dry_run':True})
