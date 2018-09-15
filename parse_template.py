# encoding=utf8
import re
import copy
from file_handle_re import CFileReader


class CTemplateParse(CFileReader):
	__PARSE_MODE_NORMAL = 1
	__PARSE_MODE_ARRAY = 2
	__PARSE_MODE_METHOD_BODY = 3
	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, CFileReader.MODE_READ_CONTENT)
		self.m_array_buf = []
		self.m_method_body_buf = []
		self.m_parse_mode = CTemplateParse.__PARSE_MODE_NORMAL
		self.m_tmp_list = []
		self.m_info_list = []

	def read_content(self, content, encoding):
		# content = re.sub(r"[\n\r]", "", content)
		self.__parse(content)

	def __parse(self, content):
		normal_parser = self.__parse_normal()
		array_parser = self.__parse_array()
		method_body_parser = self.__parse_method_body()
		for byte in content:
			if self.m_parse_mode == CTemplateParse.__PARSE_MODE_NORMAL:
				normal_parser(byte)
			elif self.m_parse_mode == CTemplateParse.__PARSE_MODE_ARRAY:
				array_parser(byte)
			elif self.m_parse_mode == CTemplateParse.__PARSE_MODE_METHOD_BODY:
				method_body_parser(byte)
		self.__combination()

	def __combination(self):
		length = len(self.m_tmp_list)
		for i in range(0, length - 1, 2):
			self.m_info_list.append(tuple(self.m_tmp_list[i: i + 2]))
		if length % 2 != 0:
			self.m_info_list.append((None, self.m_tmp_list[-1]))

	def __parse_normal(self):
		mul_buf = []
		single_buf = []
		def clear_queue():
			mul_buf.clear()
			single_buf.clear()
		def func(byte):
			single_buf.append(byte)
			if byte == " ":
				mul_buf.append("".join(single_buf))
				single_buf.clear()
			elif byte == "{":
				clear_queue()
				self.m_parse_mode = CTemplateParse.__PARSE_MODE_METHOD_BODY
			elif byte == "[" or byte == "(":
				tmp = "".join(mul_buf)
				tmp = self.__mulspace_to_singlespace(tmp).strip()
				if tmp == "if":
					clear_queue()
					self.m_parse_mode = CTemplateParse.__PARSE_MODE_ARRAY
				elif tmp == "else if":
					clear_queue()
					self.m_parse_mode = CTemplateParse.__PARSE_MODE_ARRAY
			else:
				pass
		return func

	def __parse_array(self):
		mul_buf = []
		single_buf = []
		def clear_queue():
			mul_buf.clear()
			single_buf.clear()
		def func(byte):
			if byte != "]" and byte != ")" and byte != ",":
				single_buf.append(byte)
			if byte == "]" or byte == ")":
				mul_buf.append(self.__del_white("".join(single_buf)))
				self.m_tmp_list.append(copy.copy(mul_buf))
				clear_queue()
				self.m_parse_mode = CTemplateParse.__PARSE_MODE_NORMAL
			elif byte == ",":
				mul_buf.append(self.__del_white("".join(single_buf)))
				single_buf.clear()
		return func

	def __parse_method_body(self):
		buf = []
		brace_queue = [1]
		def clear_queue():
			buf.clear()
			brace_queue.clear()
			brace_queue.append(1)
		def func(byte):
			if len(brace_queue) == 0:
				method_body = "".join(buf)
				self.m_tmp_list.append(method_body)
				clear_queue()
				self.m_parse_mode = CTemplateParse.__PARSE_MODE_NORMAL
			if byte == "{":
				brace_queue.append(1)
			elif byte == "}":
				brace_queue.pop()
			if (len(brace_queue) == 0 and byte == "}") is False:
				buf.append(byte)
		return func

	def __mulspace_to_singlespace(self, string):
		return re.sub(r"[ ]+", " ", string)

	def __del_white(self, string):
		return re.sub(r"\s", "", string)

	def read_line(self, content, encoding):
		pass

	def read_end(self):
		pass

	def __del_white_char(self, content):
		return re.sub(r"\s", "", content)

	def is_del_comment_annotation(self):
		return True

	def is_del_pound_annotation(self):
		return True

	def is_del_mul_annotation(self):
		return True

	def get_info_list(self):
		return self.m_info_list


if __name__ == "__main__":
	parser = CTemplateParse("../create_mos_svr/template/test.tml")
	parser.read()
	info_list = parser.get_info_list()
	print(info_list)
