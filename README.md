# HtmlFuck

Python program to convert an image into HTML/ascii and hide a text using brainfuck code

Pablo Marcos - 2017 

Usage
------------
```bash
> ./htmlfuck.py
```
```
usage: htmlfuck.py [-h] [-u] [-s] [-c] [-f FONT] [-t TEXT] [-tf TEXTFILE]
                   [-a ALPHABET]
                   image file x y

Create an html image an hide a text in brainfuck code.

positional arguments:
  image                 image path/url
  file                  output file
  x                     width of image in characters
  y                     height of image in characters

optional arguments:
  -h, --help            show this help message and exit
  -u, --url             download image from url
  -s, --css             Uses css classes instead of inline styles
  -c, --clear           dont use brainfuck to hide the text
  -f FONT, --font FONT  font size in px
  -t TEXT, --text TEXT  text to hide
  -tf TEXTFILE, --textfile TEXTFILE
                        file with text to hide
  -a ALPHABET, --alphabet ALPHABET
                        characters to build the image

```
Example
------------
```
> ./htmlfuck.py -u -t "PabloMarcos2017" https://github.com/pablomm/htmlfuck/blob/master/example/example.jpg?raw=true  example.html 75 37
```

License
-------

GPLv3
