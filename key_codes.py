#!/usr/bin/python

# Script generate a key_map.h file for dFilter driver

import sys
import optparse

__author__ = "Pavel Berejnoy"

key_map = {
		0   : 0x52, 1   : 0x4f, 2   : 0x50, 3   : 0x51, 4   : 0x4b,
		5   : 0x4c, 6   : 0x4d, 7   : 0x47, 8   : 0x48, 9   : 0x49,
		'sp': 0x39, '.' : 0x34, ',' : 0x33, '?' : 0xb5, '!' : 0x82,   # sp == space
		'\"': 0xa8, '\'': 0x28, ':' : 0xa7, ';' : 0x27, '\\': 0x2b,
		'/' : 0x35, '|' : 0xab, '*' : 0x37, '-' : 0x4a, '+' : 0x4e,
		'=' : 0x0d, '(' : 0x8a, ')' : 0x8b, '[' : 0x1a, ']' : 0x1b,
		'{' : 0x9a, '}' : 0x9b, '&' : 0x88, 'a' : 0x1e, 'b' : 0x30,
		'c' : 0x2e, 'd' : 0x20, 'e' : 0x12, 'f' : 0x21, 'g' : 0x22,
		'h' : 0x23, 'i' : 0x17, 'j' : 0x24, 'k' : 0x25, 'l' : 0x26,
		'm' : 0x32, 'n' : 0x31, 'o' : 0x18, 'p' : 0x19, 'q' : 0x10,
		'r' : 0x13, 's' : 0x1f, 't' : 0x14, 'u' : 0x16, 'v' : 0x2f,
		'w' : 0x11, 'x' : 0x2d, 'y' : 0x16, 'z' : 0x2c, '0' : 0x0b,
		'1' : 0x02, '2' : 0x03, '3' : 0x04, '4' : 0x05, '5' : 0x06,
		'6' : 0x07, '7' : 0x08, '8' : 0x09, '9' : 0x0a }

src_dir = "."
conf_file = "./key_map.conf"
header_file = "key_map.h"

def add_line(key, values):
	v_str = ""
	for v in values:
		v_str += "0x{0:x}, ".format(v)
	v_str = v_str[:-2]
	return "KEY(0x{0:x}, {1}, {2}), \\\n".format(key, len(values), v_str)

def process_line(line, lineno, useKeys = False):
	if len(line.strip()) == 0:
		return 0
	key = None
	values = []
	comment = False
	for word in line.split():
		word = word.strip()
		if word[0] == "#":
			comment = True
			break
		if word == "->":
			if key is None:
				print("Error at line {0}: key_code not found\n\t{1}\n".format(lineno, line))
				return 1
		elif word in key_map.keys():
			if key is None:
				try:
					word = int(word)
				except TypeError:
					print("Error at line {0}: key {1} is incorrect".format(lineno, key))
					return 1
				if useKeys:
					key = word
				else:
					key = key_map[word]
			elif useKeys:
				values.append(word)
			else:
				values.append(key_map[word])	
		else:
			print("Error at line {0}: key {1} not found in map\n\t{2}\n".format(lineno, word, line))
			return 1
	if comment and key is None:
		return 0

	if key is None:
		print("Error at line {0}: key not found\n\t{1}\n".format(lineno, line))
		return 1
	if len(values) == 0:
		print("Error at line {0}: no new key codes found\n\t{1}\n".format(lineno, line))
		return 1
	return key, values

def gen_keymap():
	# Файл конфигурации должен содержать пары вида: key_code -> new_key_codes
	lineno = 0
	max_len = -1
	result = ""
	count = 0

	try:
		result_file = open(src_dir + "/" + header_file, "w")
	except(IOError):
		print("Error while openning file {0}/key_map.h".format(src_dir))
		return 1

	line_wroten = False
	
	try:
		for line in open(conf_file, "r"):
			lineno += 1
			r = process_line(line, lineno)
			try:
				r = int(r)
				if r == 0:
					continue
				else:
					return r
			except TypeError:
				key, values = r

			if not line_wroten:
				line_wroten = True
				result += "/** Keys generated by {0} script.\n".format(sys.argv[0][2:])
				result += "  * Author Pavel Berejnoy\n  */\n\n"
				result += "#define KEY_MAP { \\\n"
			result += add_line(key, values)
			count += 1
	
			if max_len < len(values):
				max_len = len(values)

		if not line_wroten:
			print("File key_map.conf can not be processed")
			return 1

		result = result[:-4] + "\\\n}\n\n"
		result += "#define MAX_CODES {0}\n".format(max_len)
		result += "#define KEYS_COUNT {0}\n".format(count)
		result_file.write(result)
	except(IOError):
		print("File key_map.conf not found")
		return 1
	return 0

def format(l):
	if len(l) > 5:
		return "***"
	s = ""
	for item in l:
		if item == "sp":
			item = ",_,"
		s += "{0}".format(item)
	return s

def show_keys(d):
	ss = "-" * 25 + "\n"
	sss = "|" + " " * 7 + "|" + " " * 7 + "|" + " " * 7 + "|\n"
	sss = ""
	s = ss

	f_str = "|{0:^7}|{1:^7}|{2:^7}|\n"
	large_lines = []
	for i in range(6, -1, -3):
		i += 1
		for j in range(i, i + 3):
			if len(d[j]) > 5:
				large_lines.append(d[j])

		s += sss + f_str.format(i, i + 1, i + 2) + sss + ss + sss
		s += f_str.format(format(d[i])     if i     in d.keys() else "",
						  format(d[i + 1]) if i + 1 in d.keys() else "",
						  format(d[i + 2]) if i + 2 in d.keys() else "")
		s += sss + ss

	if 0 in d.keys():
		ss = " " * 8 + "|" + " " * 7 + "|\n"
		if sss == "":
			ss = ""
		s += ss
		f_str = " {0:^7}|{1:^7}|{2:^7}\n"
		s += f_str.format("", 0, "") + ss
		s += " " * 8 + "|" + "-" * 7 + "|\n" + ss
		s += f_str.format("", format(d[0]), "") + ss
		s += " " * 8 + "|" + "-" * 7 + "|\n"

	if len(large_lines) != 0:
		for line in large_lines:
			s += "\n*** -> "
			for item in line:
				if item == "sp":
					item = ",_,"
				s += "{0}".format(item)
	
	print(s + "\n,_, == <space>")

def show_codes():
	line_no = 0
	r_dict = {}
	try:
		for line in open("key_map.conf", "r"):
			line_no += 1
			r = process_line(line, line_no, True)
			try:
				r = int(r)
				if r == 0:
					continue
				else:
					return r
			except(TypeError):
				key, vals = r

			r_dict[key] = vals

	except(IOError):
		print("File key_map.conf not found")
		return 1
	
	show_keys(r_dict)

def parse_args():
	parser = optparse.OptionParser(usage="Usage: %prog [options]\n",
								   description="Create or show current keymap.\n"
								   		"Program needs a ./key_map.conf file with current keymap configuration.\n\n"
										"%prog [without options] will show current keymap.")
	parser.add_option("-g", "--gen", dest="generate", default=None,
					  help="Generate new keymap", action="store_true")
	parser.add_option("-s", "--sourcedir", dest="srcdir", default=".",
					  help="Contents source directory path where generated file will be added [default: .]. "
					  	   "This option can be used only with --gen option.")
	parser.add_option("-c", "--conffile", dest="conffile", default="./key_map.conf",
					  help="Configuration file name with full path [default: ./keymap.conf]")
	parser.add_option("-o", "--out", dest="header", default="key_map.h",
					  help="Generated file name [default: key_map.h]. "
					  	   "This option can be used only with --gen option.")
	parser.add_option("-k", "--keymap", dest="keymap", default=None,
					  help="Show info about configuration file", action="store_true")

	return parser.parse_args()

def run():
	opts, args = parse_args()

	global conf_file, header_file, src_dir

	conf_file = opts.conffile;
	header_file = opts.header;
	src_dir = opts.srcdir;

	if opts.keymap:
		print("./key_map.conf file format:\n\t"
			  "Old_key_{0..9 numbers} -> new_keys_{symbols from alphabet* splitted by space}\n" +
			  "*You can find this alphabet in {0} module.".format(sys.argv[0]))
		return

	if (not opts.generate) and (opts.srcdir != "." or opts.header != "key_map.h"):
		print("You can't use --sourcedir or --out options without --gen option.")
		return

	if opts.generate:
		if gen_keymap() == 0:
			print("Keymap generated successfully")
		return

	show_codes()

if __name__ == "__main__":
	run()
