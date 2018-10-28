# encoding=utf8
import re
from file_handle_re import CFileReader


class CDefineParse(CFileReader):
	NAMESPACE = "namespace"
	BEGIN = "begin"
	BREF = "bref"
	URL = "url"
	CLASS_INFO = "class_info"
	CLASS_LIST = "class_list"
	CLASS_NAME = "class_name"
	METHOD = "method"
	INPUT_PARAMS = "input_params"
	OUTPUT_PARAMS = "output_params"
	PARAM_TYPE = "param_type"
	PARAM_NAME = "param_name"
	IO_PARAM_TYPE = "io_param_type"
	PARAM_TYPE_URLPARAM = "params"
	PARAM_TYPE_HEADER = "header"
	PARAM_TYPE_BODY = "body"
	PARAM_TYPE_PATH = "PATH"
	PARAM_TYPE_CONTEXT = "context"
	__KEYWORD_BREF = "@bref"
	__KEYWORD_CLASSNAME = "@classname"
	__KEYWORD_METHOD = "@method"
	__KEYWORD_URL = "@url"
	__KEYWORD_IN = r"@in"
	__KEYWORD_OUT = r"@out"
	__P = "p"
	__H = "h"
	__B = "b"
	__U = "u"
	__C = "c"

	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, CFileReader.MODE_READ_CONTENT)
		self.m_info_dict = {}

	def read_content(self, content, encoding):
		# 获取 namespace
		namespace = re.findall(r"(?:^|[\s]*?)#[ ]*?namespace[ ]+?(.*)?", content)
		if len(namespace) == 0:
			raise SystemExit("[Namespace Error] namespace is none")
		namespace = namespace[-1]
		# 获取 begin
		begin = re.findall(r"(?:^|[\s]*?)#[ ]*?begin[ ]+?(.*)?", content)
		if len(begin) == 0:
			raise SystemExit("[Begin Error] begin is none")
		begin = begin[-1]
		# 获取 注释体 和 语句体
		class_list = []
		find_result = re.findall(r"\/\*(.*?)\*\/.*?", content, re.S)
		for result in find_result:
			anno_block = result
			bref, class_name, input_params, output_params, url, method = self.__parse_anno_block(anno_block)
			if class_name is None:
				print("[Warning] is not exist classname")
				continue
			class_info = {}
			class_info[CDefineParse.CLASS_NAME] = class_name
			if method is None:
				method = "post"
			class_info[CDefineParse.METHOD] = method.lower()
			if bref is not None:
				class_info[CDefineParse.BREF] = bref
			if url is not None:
				class_info[CDefineParse.URL] = url
			if input_params is not None:
				class_info[CDefineParse.INPUT_PARAMS] = input_params
			if output_params is not None:
				class_info[CDefineParse.OUTPUT_PARAMS] = output_params
			class_list.append(class_info)
		self.m_info_dict[CDefineParse.NAMESPACE] = namespace
		self.m_info_dict[CDefineParse.BEGIN] = begin
		self.m_info_dict[CDefineParse.CLASS_LIST] = class_list

	def __parse_anno_block(self, anno_block):
		bref = None
		class_name = None
		method = None
		url = None
		input_params = []
		output_params = []
		lines = anno_block.splitlines()
		for line in lines:
			if line == "":
				continue
			is_keyword = self.__is_keyword(CDefineParse.__KEYWORD_BREF, line)
			if is_keyword is not None:
				bref = is_keyword
			is_keyword = self.__is_keyword(CDefineParse.__KEYWORD_CLASSNAME, line)
			if is_keyword is not None:
				class_name = is_keyword
			is_keyword = self.__is_keyword(CDefineParse.__KEYWORD_METHOD, line)
			if is_keyword is not None:
				method = is_keyword
			is_keyword = self.__is_keyword(CDefineParse.__KEYWORD_URL, line)
			if is_keyword is not None:
				url = is_keyword
			is_find, _type, param_str = self.__param_is_keyword(CDefineParse.__KEYWORD_IN, line)
			if is_find is True:
				tmp = self.__parse_param_str(_type, param_str)
				if tmp is not None:
					input_params.append(tmp)
			is_find, _type, param_str = self.__param_is_keyword(CDefineParse.__KEYWORD_OUT, line)
			if is_find is True:
				tmp = self.__parse_param_str(_type, param_str)
				if tmp is not None:
					output_params.append(tmp)
		if len(input_params) == 0:
			input_params = None
		if len(output_params) == 0:
			output_params = None
		return bref, class_name, input_params, output_params, url, method

	def __parse_param_str(self, _type, param_str):
		search = re.search(r"(.*?):(.*)?", param_str)
		gropus = search.groups()
		search_len = len(gropus)
		if search_len != 2:
			raise SystemExit("[Param Error] {0} (not exist ':' between param_name and param_type)".format(param_str))
		tmp = {}
		tmp[CDefineParse.PARAM_NAME] = self.__del_white_char(gropus[0])
		tmp[CDefineParse.PARAM_TYPE] = self.__del_white_char(gropus[1])
		_type = self.__del_white_char(_type)
		if _type == CDefineParse.__B:
			_type = CDefineParse.PARAM_TYPE_BODY
		elif _type == CDefineParse.__H:
			_type = CDefineParse.PARAM_TYPE_HEADER
		elif _type == CDefineParse.__P:
			_type = CDefineParse.PARAM_TYPE_URLPARAM
		elif _type == CDefineParse.__U:
			_type = CDefineParse.PARAM_TYPE_PATH
		elif _type == CDefineParse.__C:
			_type = CDefineParse.PARAM_TYPE_CONTEXT
		tmp[CDefineParse.IO_PARAM_TYPE] = _type
		return tmp

	def __param_is_keyword(self, keyword, content):
		search = re.search(keyword + r"(.*?)\[(.*?)\][ ]+?(.*)?", content)
		if search is None:
			return False, None, None
		groups = search.groups()
		length = len(groups)
		if length != 3:
			return False, None, None
		return True, groups[1], groups[2]

	def __is_keyword(self, keyword, content):
		reg = r"[ ]+?(.*)?"
		search = re.findall(keyword + reg, content)
		length = len(search)
		if length > 0:
			return search[0]
		return None

	def __del_white_char(self, content):
		return re.sub(r"\s", "", content)

	def is_del_comment_annotation(self):
		return False

	def is_del_pound_annotation(self):
		return False

	def get_info_dict(self):
		return self.m_info_dict


if __name__ == "__main__":
	parser = CDefineParse("../create_cbf_frame/file/test.de")
	parser.read()
	info_dict = parser.get_info_dict()
	print(info_dict)
