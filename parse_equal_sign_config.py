# encoding=utf8
import re
from file_handle_re import CFileReader


class CEqualSignConfigParse(CFileReader):
	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, CFileReader.MODE_READ_LINE)
		self.m_info_dict = {}

	def read_line(self, content, encoding):
		if content == "":
			return
		info_list = re.findall(r"(?:^|[ |\s]*?)(.*?)[ |\s]*?=[ |\s]*?(.*)?", content)
		for info_tuple in info_list:
			if len(info_tuple) != 2:
				continue
			key, value = info_tuple
			key = self.__del_white_char(key)
			value = self.__del_white_char(value)
			self.m_info_dict[key] = value

	def read_end(self):
		pass

	def __del_white_char(self, content):
		return re.sub(r"\s", "", content)

	def is_del_comment_annotation(self):
		return True

	def is_del_pound_annotation(self):
		return True

	def get_infos(self):
		return self.m_info_dict

	def is_del_mul_annotation(self):
		return True


if __name__ == "__main__":
	parser = CEqualSignConfigParse("../create_mos_svr/config.txt")
	parser.read()
	infos = parser.get_infos()
	print(infos)
