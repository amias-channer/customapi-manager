import CustomAPI

regex = '\\r\\n|\\n|\\r'
double_quote = '''"'''
single_quote = "'"

head1 = """
<html>
<head>
<style>
body {
  font-family: helvetica, sans-serif;
  font-size: 20px;
}
</style>
<script>
function crToComma(){
	var textarea = document.getElementById('data');
    var content = textarea.value.replace(/(""" + regex + """)/gm, ',');
	textarea.value = content;
}

function spacesToComma(){
	var textarea = document.getElementById('data'); 
    var content = textarea.value.replace(/(\s)/gm, ','); 
    textarea.value = content;
}
function noSingleQuotes(){
	var textarea = document.getElementById('data'); 
    var content = textarea.value.replace(/(""" + single_quote + """)/gm, ''); 
    textarea.value = content;
}

function noDoubleQuotes(){
	var textarea = document.getElementById('data'); 
    var content = textarea.value.replace(/(""" + double_quote + """)/gm, ''); 
    textarea.value = content;
}

function noDupes(){
	var textarea = document.getElementById('data'); 
    var content = textarea.value.replace(/(\W{2,})/gm, ''); 
    textarea.value = content;
}

function clearChannel(){
    var channel = document.getElementById('channel');
    channel.value = ' ';
}
</script>
<body>
<font size="+5">&nbsp;<b>CustomAPI</b></font><br>
<font size="-1">
&nbsp;&nbsp;&nbsp;&nbsp;[ <a href="/user">"""
head2 = """</a> ] [ <a href="/start">Your APIs</a> ] [ <a href="/shared">Shared APIs</a> ]"""
head3 = """ [ <a href="/logout">Logout</a> ]
</font>
<br><br>
"""
head = head1 + "You" + head2 + head3
loginform = """
<form action='/start' method='get'><br><br>
    This is a private system , please ask Amias for a login.<br><br>
    <input type='submit' value='Login'>
</form>"""
foot = """<br><br><font size='-6'><a href="https://amias.net/">Amias Channer© 2024 </a></font></body></html>"""


def header(user: CustomAPI.User):
    if user.admin:
        admin = """[ <a href="/admin">Admin</a> ]"""
    return head1 + user.name + head2 + admin + head3
