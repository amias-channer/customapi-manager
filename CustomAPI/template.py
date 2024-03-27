
regex = '\\r\\n|\\n|\\r'
double_quote = '''"'''
single_quote = "'"

head = """
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
<font size="+5"><b>CustomAPI</b></font><br>
&nbsp;&nbsp;[ <a href="/logout">Logout</a> ] [ <a href="/start">APIs</a> ] [ <a href="/admin">Admin</a> ] 
<br><br>
"""
loginform = """
<form action='/start' method='get'>
    This is a private system , please ask Amias for a login.<br>
    <input type='submit' value='Login'>
</form>"""
foot = """<br><br><font size='-6'><a href="https://amias.net/">Amias Channer© 2024 </a></font></body></html>"""
