import CustomAPI

regex = '\\r\\n|\\n|\\r'
double_quote = '''"'''
single_quote = "'"

head1 = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
  font-family: helvetica, sans-serif;
  font-size: 20px;
}
</style>
<script>
function crToDelimiter(){
    var textarea = document.getElementById('data');
    var delimiter = document.getElementById('delimiter');
    var content = textarea.value.replace(/(""" + regex + """)/gm, delimiter.value);
    textarea.value = content;
}

function spacesToDelimiter(){
    var textarea = document.getElementById('data'); 
    var delimiter = document.getElementById('delimiter');
    var content = textarea.value.replace(/(\s)/gm, delimiter.value); 
    textarea.value = content;
}

function toggleReplacementsMenu(){
    var menu = document.getElementById('replacements');
    if (menu.style.display == 'none'){
        menu.style.display = 'inline';        
    } else {
        menu.style.display = 'none';
    }
}

function removeCharacters(option, replacement){
    if ( replacement == undefined ) {
        replacement = document.getElementById('delimiter').value;
    }
    const options = new Map();
    options.set('cr', '""" + regex + """');
    options.set('spaces', "\s");
    options.set('single_quotes', ",");
    options.set('double_quotes', ",");
    options.set('parentheses', "[\{|\}]");
    options.set('brackets', "[\(|\)]");
    options.set('square', "[\[|\]]");
    options.set('angle', "[\<|\>]");
    options.set('dupes', "(\W)\2+");
    regex = new RegExp(options.get(option), 'gm');
    var textarea = document.getElementById('data');
    var content = textarea.value.replace(regex, replacement);
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
head = head1 + "You </a> " + head3
loginform = """
<form action='/start' method='get'><br><br>
    This is a private system , please ask Amias for a login.<br><br>
    <input type='submit' value='Login'>
</form>"""
foot = """<br><br><font size='-6'><a href="https://amias.net/">Amias Channer© 2024 </a></font></body></html>"""


def header(user: CustomAPI.User):
    admin = ""
    if user.admin:
        admin = """[ <a href="/admin">Admin</a> ]"""
    return head1 + user.name + head2 + admin + head3
