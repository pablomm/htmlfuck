from __future__ import print_function

import random
import requests
from StringIO import StringIO
from PIL import Image


"""
TODO
Buscar coeficiente font-size ~ size en pixeles
Agrupar spans vecinos con mismo color (funcion a medio hacer)
Permitir que size sea un argumento opcional tomando el original de la imagen en su lugar
Control de excepciones
Documentacion
"""


def get_rgb_image(img_name, size):
	
	im = Image.open(img_name)


	im_resized = im.resize(size, Image.ANTIALIAS)

	return im_resized.convert('RGB').load()



def get_random_vector(alphabet, size):
	x, y = size
	vector = [random.choice(alphabet) for _ in xrange(x*y)]

	return vector


def hide_positions(vector_len, text_len):

	positions = range(vector_len)
	random.shuffle(positions)

	positions = positions[0:text_len]
	positions.sort()

	return positions

def hide_text(vector, text):

	positions = hide_positions(len(vector), len(text))

	j=0
	for i in positions:
		vector[i] = text[j]	
		j = j+1

	return vector

def write_header(file, font_size=None):
	style = "" if font_size== None else " style='font-size: %dpx'" % font_size
	file.write("<center>\n\t<!-- Pablo Marcos - 2017 -->\n\t<pre%s>" % style)

def write_span(file, rgb, text):
	hexcolor = '#%02x%02x%02x' % rgb
	file.write("<span style='color: %s;'>%s</span>" % (hexcolor,text))

def write_footer(file):
	file.write("</pre>\n</center>")

def write_span_line(size_x,y,file,vector,img):
	back = size_x * y
	x=0
	while x < size_x:
		text = str(vector[back + x])
		while x < size_x-1:
			if img[x,y] == img[x+1,y]:
				x = x+1
				text = str(vector[back + x])
			else:
				break
				
		write_span(file,img[x,y],text)

	file.write("<br />")	

def write_html_document(filename, img, vector, size,font_size=None):
	 
	size_x, size_y = size

	with open(filename,"w") as file:
	 	write_header(file,font_size)

	 	for y in xrange(size_y):
	 		for x in xrange(size_x):
	 			write_span(file,img[x,y],vector[y*size_x + x])
	 		file.write("<br />")

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


def example():

	size = 100, 50
	alphabet = ";:()$!#="
	hide_text = "PABLOMARCOS"
	url = "https://pbs.twimg.com/profile_images/2579154910/jlhbzolim7run4t9hs6y_400x400.gif"
	font_size = None
	is_url = True

	generate_html_image(url, "test.html", alphabet, hide_text, size, font_size, is_url)

if __name__ == "__main__":
	example()

