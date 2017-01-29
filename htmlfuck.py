#!/usr/bin/python

from __future__ import print_function

import argparse
import random
import requests

from sys import exit
from StringIO import StringIO
from PIL import Image
from math import copysign, ceil, floor, sqrt

__author__ = "Pablo Marcos"
__message__ = "Generated using htmlfuck - Pablo Marcos"
__description__ = "Create an html image an hide a text in brainfuck code."

"""
TODO
Buscar coeficiente font-size ~ size en pixeles
Agrupar spans vecinos con mismo color (funcion a medio hacer)
Permitir que size sea un argumento opcional tomando el original de la imagen en su lugar
Control de excepciones/ errores
Mejorar funcion genera codigo brainfuck
getopt
Documentacion
"""

def get_rgb_image(img_name, size):
	"""
	Return a matrix with the input size with
	the rgb values of the image
	"""
	try:
		im = Image.open(img_name)
	except IOError:
		print("Error opening image file: %s" % img_name)
		exit(2)

	im_resized = im.resize(size, Image.ANTIALIAS)

	return im_resized.convert('RGB').load()



def get_random_vector(alphabet, size):
	"""
	Return a list of length x*y where size = (x,y)
	initializated with pseudorandom values of the alphabet
	"""
	x, y = size
	vector = [random.choice(alphabet) for _ in xrange(x*y)]

	return vector


def hide_positions(vector_len, text_len):
	""" 
	Return a list of length text_len with not 
	repeated random values in the range vector_len
	"""
	positions = range(vector_len)
	random.shuffle(positions)

	positions = positions[0:text_len]
	positions.sort()

	return positions

def hide_text(vector, text):
	"""
	Hide the text in random positions of the vector
	and return a list
	"""
	positions = hide_positions(len(vector), len(text))

	j=0
	for i in positions:
		vector[i] = text[j]	
		j += 1

	return vector

def write_header(file, font_size=None):
	""" Write the html tags before the image """
	style = "" if font_size== None else " style='font-size: %dpx'" % font_size
	file.write("<center>\n\t<!-- %s -->\n\t<pre%s>" % (__message__,style))


def write_span(file, rgb, text):
	""" Writes a span with the rgb color and the text """
	hexcolor = '#%02x%02x%02x' % rgb
	file.write("<span style='color: %s;'>%s</span>" % (hexcolor,text))


def write_footer(file):
	""" Write the html tags after the image """
	file.write("</pre>\n</center>")


def write_span_line(size_x,y,file,vector,img):
	back = size_x * y
	x=0
	while x < size_x:
		text = str(vector[back + x])
		while x < size_x-1:
			if img[x,y] == img[x+1,y]:
				x += 1
				text = str(vector[back + x])
			else:
				break
				
		write_span(file,img[x,y],text)

	file.write("<br/>")	


def write_html_document(filename, img, vector, size,font_size=None):
	 
	size_x, size_y = size

	with open(filename,"w") as file:
	 	write_header(file,font_size)

	 	for y in xrange(size_y):
	 		for x in xrange(size_x):
	 			write_span(file,img[x,y],vector[y*size_x + x])
	 		file.write("<br/>")

	 	write_footer(file)

def parse_url(path,is_url):
	if not is_url:
		return path
	else:
		response = requests.get(path)
		return StringIO(response.content)

def generate_html_image(img_path, file_name, alphabet, text, size,font_size=None, is_url=False):
	img_name = parse_url(img_path, is_url)
	img = get_rgb_image(img_name, size)
	vector = hide_text(get_random_vector(alphabet, size) ,text)
	write_html_document(file_name, img, vector,size,font_size)



def bf_num(n):
	""" Return brainfuck code that adds n """

	code = ""
	c = "+" if copysign(1,n) == 1 else "-"

	for _ in range(abs(n)):
		code = code + c

	return code

def bf_mult(x,y):
	""" Return the brainfuck code of x*y """

	code = bf_num(abs(x))
	code += "[>"
	code += bf_num(int(copysign(1,x*y))*abs(y))
	code += "<-]>"

	return code

def bf_tuple(x,y,z,pos=2):
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
		code = code + bf_num(x)
	else:
		if pos == 2:
			code += "<"

		code += bf_mult(x,y)

	code += bf_num(z) + "."

	return code

def get_tuple(n,pos=2):
	"""
	Return brainfuck code that sum n to the second 
	brainfuck cell and print the value.

	For n>9 the problem consist in find x,y,z
	that minimizes x + y + z over the integers with
	x*y+z = n

	Thats a poor implementation, only optimal for perfect
	squares in general, takes x,y the numbers nearest to the
	square root of n and z = n - x*y, with the special case when
	the loop is not needed
	"""

	absn = abs(n)
	sign = int(copysign(1,n))
	sq = sqrt(absn)
	x = int(floor(sq))
	y = int(ceil(sq))
	z = absn - x*y

	if x + y + z + 5 > absn:
		return bf_tuple(n,1,0,pos)

	return bf_tuple(x,sign*y,sign*z,pos)

def brainfuck_ascii(text):
	"""
	Return brainfuck code that prints the input text.
	The text has to be pure ascii.
	"""

	if len(text) <1:
		return ""

	value = ord(text[0])
	code = get_tuple(value, 1)


	for letter in text[1:len(text)]:

		dif = ord(letter) - value
		value = ord(letter)
		code += get_tuple(dif)


	return code


def html_brainfuck(image,file, alphabet, text,size,font_size, is_url, clear,text_file):

	if text_file:
		try:
			tfile = open(text_file)
			text = tfile.read()
		except IOError:
			print("Error opening text file: %s" % text_file)
			exit(2)
			

	if not text:
		text = ""
	else:
		hide_text = text if clear else brainfuck_ascii(text)

	generate_html_image(image, file, alphabet, hide_text, size, font_size, is_url)

def main():
	parser = argparse.ArgumentParser(description=__description__)
	parser.add_argument('image', help='image path/url')
	parser.add_argument('file', help='output file')
	parser.add_argument('x', help="width of image in characters", type=int)
	parser.add_argument('y', help="height of image in characters", type=int)
	parser.add_argument('alphabet', help="alphabet")
	parser.add_argument("-u","--url", help="download image from url", action="store_true")
	parser.add_argument("-c","--clear", help="dont use brainfuck to hide the text", action="store_true")
	parser.add_argument("-f","--font", help="font size in px", type=int)
	parser.add_argument("-t","--text", help="text to hide")
	parser.add_argument("-tf","--textfile", help="file with text to hide")

	args = parser.parse_args()

	if args.text and  args.textfile:
		print("--text and --textfile are mutually exclusive ...")
		exit(2)

	size = args.x, args.y

	html_brainfuck(args.image,args.file, args.alphabet, args.text, size,args.font, args.url, args.clear,args.textfile)
	

if __name__ == "__main__":
	main()

