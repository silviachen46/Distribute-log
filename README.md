# Distribute-log

## overall structure:

Built with fastapi, using exclusive lock to deal with concurrent write operations.

Chosed to use simple exclusive lock instead of read-write lock since I applied lazy update mechanism(on removing outdated messages) which requires modifications in query api, thus we can't use read lock directly.

Used a dictionary with service name being the key and a SortedDict as the corresponding value to store the timestamp - message kv pair. This would have a insert time of O(logN)

For the query api I used bisect function which is of runtime of O(logN) because the key(timestamp) is in order.

I used lazy update - removing all outdated messages whenever the corresponding service is queried. This ensures data integrity and avoid edge cases compared with fixed-time automatic updates.

## instruction to run:

install dependencies if missing using pip install -r requirements.txt

run the file and it will start the service on port 8088

# Some starter curl commands to run:

collect log:

curl -X POST http://localhost:8088/logs \
  -H "Content-Type: application/json" \                      
  -d '{"service_name": "auth-service", "timestamp": "2025-03-29T19:31:07Z", "message": "Logged in successfully"}'

query log:

curl "http://localhost:8088/logs?service=auth-service&start=2025-03-29T19:28:00Z&end=2025-03-29T19:30:00Z"




