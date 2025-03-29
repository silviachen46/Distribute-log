from fastapi import FastAPI
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from sortedcontainers import SortedDict
from pydantic import BaseModel
import uvicorn
from bisect import bisect_left, bisect_right

from threading import Lock
app = FastAPI()

lock_map = defaultdict(Lock)
inmemory_store = defaultdict(SortedDict) 
# service name as buckets, storing timestamp : message as k-v pair in storage


class LogRequest(BaseModel):
    service_name:str
    timestamp:datetime
    message:str


def remove_old_records(target_service):
    current_time = datetime.now(timezone.utc)
    cutoff = current_time - timedelta(hours = 1)
    remove_keys = list(target_service.irange(maximum = cutoff, inclusive = [True, False]))
    for key in remove_keys:
        del target_service[key]

@app.post("/logs")
def set_key(request:LogRequest):
    
    # creating new entries, do not have to check if key exist already
    lock = lock_map[request.service_name]
    with lock:
        inmemory_store[request.service_name][request.timestamp] = request.message
    return {"message": "stored successfully"}

# assumption: frequent logs and fewer queries compare to log request
@app.get("/logs")
def get_key(service: str, start:datetime, end:datetime):
    if service not in inmemory_store:
        return {"message": "Error : service not exist."}
    lock = lock_map[service]
    with lock:
        target_service = inmemory_store[service]
        remove_old_records(target_service) 
        # still use exclusive lock because we remove old records first everytime doing query to ensure integrity
        # even though having some tradeoffs for specific scenarios
        target_keys = list(target_service.keys())
        left_ind = bisect_left(target_keys, start)
        right_ind = bisect_right(target_keys, end)
        result = [{"timestamp": target_keys[i], "message": target_service[target_keys[i]]} for i in range(left_ind, right_ind)]
    return result

if __name__ == "__main__":
    uvicorn.run("fast:app",host="0.0.0.0",port=8088,reload=True)