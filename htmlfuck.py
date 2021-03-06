#!/usr/bin/python

from __future__ import print_function

import argparse
import random

try:
	import requests
except ImportError:
	pass

from cgi import escape
from math import ceil, copysign, sqrt
from sys import exit
from PIL import Image

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


__author__ = "Pablo Marcos"
__message__ = "Generated using HtmlFuck - Pablo Marcos"
__description__ = "Create an html image an hide a text in brainfuck code."

color_list = []


def get_rgb_image(img_name, size):
    """
    Return a matrix with the input size with
    the rgb values of the image
    """
    try:
        im = Image.open(img_name)
        im_resized = im.resize(size, Image.ANTIALIAS)
    except IOError:
        print("ERROR: can't open image file: %s" % img_name)
        exit(2)

    return im_resized.convert('RGB').load()


def get_random_vector(alphabet, size):
    """
    Return a list of length x*y where size = (x,y)
    initializated with pseudorandom values of the alphabet
    """
    x, y = size
    vector = [random.choice(alphabet) for _ in xrange(x * y)]

    return vector


def hide_positions(vector_len, text_len):
    """
    Return a list of length text_len with not
    repeated random values in the range vector_len
    """
    if text_len > vector_len:
        print(
            "ERROR: text too long, increase the characters of the image to encode the text (%d at least)" %
            text_len)
        exit(2)

    positions = range(vector_len)
    random.shuffle(positions)

    positions = sorted(positions[0:text_len])

    return positions


def hide_text(vector, text):
    """
    Hide the text in random positions of the vector
    and return a list
    """
    positions = hide_positions(len(vector), len(text))

    j = 0
    for i in positions:
        vector[i] = text[j]
        j += 1

    return vector


def write_header(file, font_size=None, css=False, filename=None):
    """ Write the html tags before the image """

    file.write("<head>\n")
    if css:
    	file.write("  <link rel='stylesheet' type='text/css' href='%s.css'>\n" % filename.split(".")[0])
    file.write("</head>\n<body>\n")


    style = "" if font_size is None else " style='font-size: %dpx'" % font_size
    file.write("<center>\n\t<!-- %s -->\n\t<pre%s>" % (__message__, style))


def write_span(file, rgb, text):
    """ Writes a span with the rgb color and the text """
    hexcolor = '#%02x%02x%02x' % rgb
    file.write("<span style='color: %s;'>%s</span>" % (hexcolor, text))

def write_span_css(file, rgb, text):
    """ Writes a span with the rgb color and the text """
    hexcolor = '#%02x%02x%02x' % rgb

    try:
    	i = color_list.index(hexcolor)
    except:
    	color_list.append(hexcolor)
    	i = len(color_list) - 1

    file.write("<span class='c%d'>%s</span>" % (i, text))


def write_footer(file):
    """ Write the html tags after the image """
    file.write("</pre>\n</center>")
    file.write("\n</body>")


def escape_html(text):
    """escape strings for display in HTML"""
    return escape(text, quote=True).replace(u'\n', u'&nbsp').replace(
        u'\t', u'&nbsp').replace(u' ', u'&nbsp;')


def write_span_line(size_x, y, file, vector, img, css=False):
    """ Write a line of the picture grouping adjacent colors """
    i = 0
    while i < size_x:
        text = vector[y * size_x + i]
        i += 1
        while i < size_x:
            if img[i - 1, y] == img[i, y]:
                text += vector[y * size_x + i]
                i += 1
            else:
                break
        if not css:
        	write_span(file, img[i - 1, y], escape_html(text))
        else:
        	write_span_css(file, img[i - 1, y], escape_html(text))

    file.write("<br/>")


def write_html_document(filename, img, vector, size, font_size=None, css=False):
    """ Writes de html document """
    size_x, size_y = size

    with open(filename, "w") as file:
        write_header(file, font_size, css, filename)

        for y in xrange(size_y):
            write_span_line(size_x, y, file, vector, img, css)

        write_footer(file)

        if css:
        	write_styles(filename)

def write_styles(filename):

    filename = filename.split(".")[0] + ".css"

    with open(filename, "w") as file:

        file.write("/* Generated using htmlfuck - Pablo Marcos */\n")
        for i in xrange(len(color_list)):
            file.write(".c%d{color:%s;}" % (i, color_list[i]))




def parse_url(path, is_url):
    """
    Downloads the image from the url if needed,
    return an object to be open by PIL
    """
    if not is_url:
        return path
    else:

        try:
            response = requests.get(path)
            obj = StringIO(response.content)
        except IOError:
            print("ERROR: can't download the image from url %s" % path)
            exit(2)

        return obj


def generate_html_image(img_path, file_name, alphabet,
                        text, size, font_size=None, is_url=False, css=False):
    """ Call all the functions relatives on the generation of the html image """
    img_name = parse_url(img_path, is_url)
    img = get_rgb_image(img_name, size)
    vector = hide_text(get_random_vector(alphabet, size), text)
    write_html_document(file_name, img, vector, size, font_size, css)


def bf_num(n):
    """ Return brainfuck code that adds n """

    code = ""
    c = "+" if copysign(1, n) == 1 else "-"

    for _ in range(abs(n)):
        code = code + c

    return code


def bf_mult(x, y):
    """ Return the brainfuck code of x*y """

    code = bf_num(abs(x))
    code += "[>"
    code += bf_num(int(copysign(1, x * y)) * abs(y))
    code += "<-]>"

    return code


def bf_tuple(x, y, z, pos=2):
    """
    Return brainfuck code that sum x*y+z to the second
    position of the tape and print the final value.
    The position 1 have to be 0. The pointer final state
    is 2. The initial state can be 1 or 2.

    pos: the initial position of the pointer (default 2)
    """

    code = ""

    if y == 1:
        if pos == 1:
            code += ">"
        code += bf_num(x)
    else:
        if pos == 2:
            code += "<"

        code += bf_mult(x, y)

    code += bf_num(z) + "."

    return code


def terna(n):
    """
    Return the optimal representation of n>0
    that minimizes |x|+|y|+|z| with n = x*y+z
    """

    absn = abs(n)
    sq = int(ceil(sqrt(absn)))

    x = 0
    y = 0
    z = absn
    peso = absn

    for i in range(sq, 1, -1):
        for j in range(sq, 1, -1):
            k = absn - i * j

            if i + j + abs(k) <= peso:
                peso = i + j + abs(k)
                x = i
                y = j
                z = k

    return (x, y, z)


def get_tuple(n, pos=2):
    """
    Return brainfuck code that sum n to the second
    brainfuck cell and print the value.
    """
    sign = int(copysign(1, n))

    x, y, z = terna(n)

    y *= sign
    z *= sign

    if x + abs(y) + abs(z) + 5 > abs(n):
        return bf_tuple(n, 1, 0, pos)

    return bf_tuple(x, y, z, pos)


def brainfuck_ascii(text):
    """
    Return brainfuck code that prints the input text.
    The text has to be pure ascii.
    """

    if len(text) < 1:
        return ""

    value = ord(text[0])
    code = get_tuple(value, 1)

    for letter in text[1:len(text)]:

        dif = ord(letter) - value
        value = ord(letter)
        code += get_tuple(dif)

    return code


def html_brainfuck(image, file, alphabet, text, x, y,
                   font_size, is_url, clear, text_file, css):
    """ Generate the image with the arguments given by argparse """

    size = x, y

    if text_file:
        try:
            tfile = open(text_file)
            text = tfile.read()
        except IOError:
            print("ERROR: can't open text file: %s" % text_file)
            exit(2)

    if not text:
        hide_text = ""
    else:
        hide_text = text if clear else brainfuck_ascii(text)

    if any(True for x in alphabet if x in ".,[]<>-+"):
        print("WARNING: your alphabet contains brainfuck characters")

    generate_html_image(image, file, alphabet, hide_text,
                        size, font_size, is_url, css)


def main():
    """
    Main function
    Parse the arguments given and show the usage
    """
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('image', help='image path/url')
    parser.add_argument('file', help='output file')
    parser.add_argument('x', help="width of image in characters", type=int)
    parser.add_argument('y', help="height of image in characters", type=int)
    parser.add_argument(
        "-u", "--url", help="download image from url", action="store_true")
    parser.add_argument(
        "-s", "--css", help="Uses css clases instead of inline styles", action="store_true")

    parser.add_argument(
        "-c", "--clear", help="dont use brainfuck to hide the text", action="store_true")
    parser.add_argument("-f", "--font", help="font size in px", type=int)
    parser.add_argument("-t", "--text", help="text to hide")
    parser.add_argument("-tf", "--textfile", help="file with text to hide")
    parser.add_argument(
        "-a", '--alphabet', help="characters to build the image", default="@#$%()/*")

    args = parser.parse_args()

    if args.text and args.textfile:
        print("ERROR: --text and --textfile are mutually exclusive ...")
        exit(2)

    html_brainfuck(args.image, args.file, args.alphabet,
                   args.text, args.x, args.y, args.font, args.url, args.clear, args.textfile, args.css)

    exit(0)


if __name__ == "__main__":
    main()
