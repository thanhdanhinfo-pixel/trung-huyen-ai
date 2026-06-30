import subprocess,sys
TOOLS=['repo_snapshot.py','dependency_graph.py','root_audit.py','orphan_detector.py','repo_tree.py','architecture_audit.py','move_recommendation.py','import_safety.py']
for t in TOOLS:
    print(f'RUN {t}')
    subprocess.call([sys.executable,f'tools/{t}']) 
print('ALL ARTIFACTS GENERATED')
