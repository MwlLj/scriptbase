# encoding=utf8
import sys
import os
sys.path.append("../base/")
from string_tools import CStringTools
from file_handle_re import CFileHandle


class CWriteFileBase(object):
	def __init__(self, file_path):
		self.m_file_handler = CFileHandle()
		self.m_file_path = file_path

	def is_debug(self):
		return True

	def implement(self):
		return ""

	def write(self, encoding="utf8"):
		content = ""
		content += self.implement()
		if self.is_debug() is True:
			print(content)
		else:
			dirname = os.path.dirname(self.m_file_path)
			if os.path.exists(dirname) is False:
				user_input = input("[Tip] dir is not exist, create ? [y/n]")
				if user_input.lower() != "y":
					raise SystemExit("[Waring] Create Failed")
				else:
					os.makedirs(dirname)
			self.m_file_handler.clear_write(content, self.m_file_path, encoding)


class __CTest(CWriteFileBase):
	def __init__(self, file_path):
		CWriteFileBase.__init__(self, file_path)

	def implement(self):
		content = ""
		content += "hello word"
		return content

	def is_debug(self):
		return True


if __name__ == "__main__":
	test = __CTest("../pdm2sql/obj/test.sql")
	test.write()
