
make a fastapi app to serve apis for twitch users

what to store data in ? 
 how much data ? 
    users: 100
    apis each: 100
    api size: 10k

 sql lite
    tables: apis, users
    
    api: id, name , data , channel
    user: id, name, password
    owners: user_id, api_id
    editors: user_id, api_id
    logins: user_id, session_id 
apis:
- create - makes a new api
- edit - edits an existing api
- delete - deletes an existing api
- api - access the api
users:
    creator - makes and owns a list
    editor - can edit a creators list
    viewer - a channel that can use an api
