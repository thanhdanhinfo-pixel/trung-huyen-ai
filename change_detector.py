def detect_changes(old_index:list,new_index:list): 
    old_ids={d["id"] for d in old_index}
    return [d for d in new_index if d["id"] not in old_ids]
