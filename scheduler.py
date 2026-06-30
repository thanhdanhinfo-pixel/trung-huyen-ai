from datetime import datetime,timedelta 

def next_run(hours:int=24):
    return (datetime.utcnow()+timedelta(hours=hours)).isoformat()
