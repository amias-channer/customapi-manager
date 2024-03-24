
Customapmi-manager is a Fastapi app to serve 'api's to stream elements commands used by twitch users in chat.

What are these api's 

You can make commands in twitch chat like this 
!cmd greetings Hello everyone 

when people then type !greetings the chat bot will reply with Hello everyone.

Here is a writeup of how these commands work.
https://github.com/amias-channer/obs-scripts/blob/master/chat.md

In these commands its possible to use a tag to fetch external data.

!cmd add weather ${customapi.weather.com/forecast?location=${queryescape ${1:}}}
!weather Amsterdam
StreamElements: Amsterdam, Netherlands: 🌞 8.0 °C (46.4 °F). Feels like 4.3 °C (39.8 °F). Light rain. Wind is blowing from the West at 31.0 km/h (19.2 mp/h). 71% humidity. Visibility: 10 km (6 miles). Air pressure: 1007 hPa.

Streamelements makes an HTTP Get request to the http://weather.com/forecast?location=Amsterdam and displays the content it gets back.

This code provides a website that lets user host and edit the data for customapi feeds.

Data is stored in a SQLite 3 file but you can just supply a different connect string and it will use another database, SQL ALchmey is very nice.

Thanks to all the open source project developers who contributed to the tools underneath all of this.



Tables
    api: id, name , data , channel
    user: id, name, password
    owners: user_id, api_id
    editors: user_id, api_id
    logins: user_id, session_id 


