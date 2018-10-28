# encoding=utf8
import sys
import os
import re
from file_handle_re import CFileReader


class CWrite(CFileReader):
	def __init__(self, path):
		CFileReader.__init__(self, path)
		self.m_file_path = path
		self.m_content = ""
		self.m_encoding = "utf8"

	def full_content(self, content):
		search = re.search(r"(?:^|[ |\s]*)#[ ]*?encoding[ ]*?=[ ]*?utf8", content)
		if search is None:
			self.m_content += "# encoding=utf8" + "\n"

	def read_line(self, content, encoding):
		self.m_encoding = encoding
		self.m_content += content + "\n"

	def read_end(self):
		# print(self.m_content)
		self.clear_write(self.m_content, self.m_file_path, self.m_encoding)


class CAddEncoding(object):
	def __init__(self, root):
		self.m_root = root

	def execute(self):
		for path, dirs, files in os.walk(self.m_root):
			for file in files:
				file_name, file_ext = os.path.splitext(file)
				if file_ext != ".py":
					continue
				self.__handle_file(os.path.join(path, file))

	def __handle_file(self, path):
		handle = CWrite(path)
		handle.read()


if __name__ == "__main__":
	args = sys.argv
	length = len(args)
	root = "."
	if length == 2:
		root = args[1]
	add = CAddEncoding(root)
	add.execute()
