# encoding=utf8
import sys
import os
import re
from file_handle_re import CFileReader


class IUpdateBase(object):
	def start_keys(self):
		# 获取开始的关键字
		return [r"/\*@@start@@\*/"]

	def seekout(self, key):
		return ""

	def parse_end(self, content):
		pass

	def mode(self):
		return CUpdateBase.MODE_WRITE_DOWN

	def is_debug(self):
		return True

	def line_content(self, content):
		pass

	def is_write(self):
		# 没读取一行, 都会调用一次, 如果返回 False, 框架将不维护本行的文本
		return True


class CUpdateBase(IUpdateBase, CFileReader):
	MODE_WRITE_TOP = 1
	MODE_WRITE_DOWN = 2
	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, line_mode=CFileReader.MODE_READ_LINE)
		self.__m_content = ""
		self.m_encoding = "utf8"

	def read_line(self, content, encoding):
		self.m_encoding = encoding
		self.line_content(content)
		if self.mode() == CUpdateBase.MODE_WRITE_DOWN:
			if self.is_write() is True:
				self.__m_content += content + "\n"
			is_find, key = self.__is_key(content)
			if is_find is True:
				tmp = self.seekout(key)
				if self.is_write() is True:
					self.__m_content += tmp
		elif self.mode() == CUpdateBase.MODE_WRITE_TOP:
			is_find, key = self.__is_key(content)
			if is_find is True:
				tmp = self.seekout(key)
				if self.is_write() is True:
					self.__m_content += tmp
			if self.is_write() is True:
				self.__m_content += content + "\n"

	def get_encoding(self):
		return self.m_encoding

	def __is_key(self, content):
		for key in self.start_keys():
			search = re.match(r".*?{0}.*?".format(key), content)
			if search is not None:
				return True, key
		return False, ""

	def read_end(self):
		self.parse_end(self.__m_content)
		if self.is_debug() is True:
			print(self.__m_content)
		else:
			self.clear_write(self.__m_content, self.get_file_path(), encoding=self.m_encoding)

	def full_content(self, content):
		pass


class __CTest(CUpdateBase):
	def __init__(self, file_path):
		CUpdateBase.__init__(self, file_path)

	def full_content(self, content):
		pass

	def start_keys(self):
		return [r"/\*@@start@@\*/", r"/\*@@push_back@@\*/"]

	def seekout(self, key):
		content = ""
		if key == r"/\*@@start@@\*/":
			content += '#include "test.h"\n'
		return content

	def parse_end(self, content):
		print(content)
		# pass


if __name__ == '__main__':
	update = __CTest("../createsvr/obj/testjson/include/testjson_common.h")
	update.read()
