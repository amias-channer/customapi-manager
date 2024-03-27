
Customapmi-manager is a Fastapi app to serve APIs to stream elements commands used by twitch users in chat.

### What are these APIs ? 

You can make commands in twitch chat like this 
```
!cmd add greetings Hello everyone
```

when people can run the command to get the response type  the chat bot will reply with Hello everyone.

```
!greetings
StreamElements: Hello everyone
```

Here is a writeup of how these commands work.<Br>
https://github.com/amias-channer/obs-scripts/blob/master/chat.md

In these commands its possible to use a tag to fetch external data.

```
!cmd add weather ${customapi.weather.com/forecast?location=${queryescape ${1:}}}
!weather Amsterdam
StreamElements: Amsterdam, Netherlands: 🌞 8.0 °C (46.4 °F). Feels like 4.3 °C (39.8 °F). 
                Light rain. Wind is blowing from the West at 31.0 km/h (19.2 mp/h). 
                71% humidity. Visibility: 10 km (6 miles). Air pressure: 1007 hPa.
```
Streamelements makes an HTTP Get request to the http://weather.com/forecast?location=Amsterdam and displays the content it gets back.

### How does this code help ?

This code provides a website that lets user host and edit data to be fed into customapi.

Consider this command, it uses a customapi feed that returns a place name from a list of 80,000 , this is used to build a text prompt which is sent to an llm to  generate a random wine description 
```
!cmd add wine ${ai make up a authentic sounding wine from ${customapi.api.amias.net/1} and describe how it tastes }
!wine
StreamElements: Introducing "Carmenella Reserva" from El Dovio a rich blend of ripe blackberries velvety chocolate and a hint of smoky oak This wine delights the palate with its smooth tannins and long elegant finish
!wine
StreamElements: Introducing Blandville Blush Enigma - a delightful blend of strawberry and hints of melon This wine offers a crisp and light finish with a touch of sweetness that lingers on the palate Truly a refreshing and harmonious experience
!wine
StreamElements: Introducing Whitehaven Chardonnay - a rich and creamy wine with notes of ripe apple and pear This wine offers a smooth and buttery finish with a hint of vanilla Truly a luxurious and indulgent experience
```

This is useful for several reasons:
* Twitch chat is not a good place to edit data in commands.
* A command can only hold 250 chars of data.
* Random selection in Steamelements is inefficient.
* Here a single element of data is randomly chosen by the server
* The data can be shared between multiple commands.
* The data can be edited by multiple users.
* The data can be restricted to certain channels
* The data can store prompt data for the {ai } tag
* The data can store scripts for the {maths } tag
* This website provides tools for formatting the data in to CSV

This website gives users a convenient way to manage this data so they
can provide impressive ranges of data in their commands.

### Data Storage

Data is stored in a SQLite 3 file in these tables

    api: id, name , data , channel, editor
    user: id, name, password, admin, enabled
    owners: user_id, api_id
    editors: user_id, api_id
    logins: user_id, session_id 

You can just supply a different connect string in database.py and SQLALchemy
will use that an rebuild the database, SQL ALchmey is very nice.

If you mess up you can just remove customapi.db and restart the app.


### Installation

This is a Fastapi app so you will need to install the requirements in requirements.txt
```
pip install -r requirements.txt
```
The database will be auto created when you run the app for the first time.
Run this line of SQL to create your first admin user.
```
insert into users (name, password, enabled, admin) values ('root', 'change this password', 1, 1);
```


The server runs on localhost 8000,  you should setup a proxy to serve to the wider internet.

Here is an example of a nginx config to serve the app on a subdomain.
```
server {
        server_name your.server.name;
        location / {
                proxy_pass http://127.0.0.1:8000;
        }
}
```
You should add SSL to protect the logins , this is easy with certbot.

### Running the app

You can run the app with uvicorn
```
uvicorn customapi:app
```
Then browse to http://127.0.0.1:8000 or the domain you have setup.

Login with the user you created and start adding APIs !

Thanks to all the open source project developers who contributed to the tools underneath all of this.






