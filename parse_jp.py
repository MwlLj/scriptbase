# encoding=utf8
import os
import re
from file_handle_re import CFileReader


class CJpParse(CFileReader):
	DICT_KEY_NAMESPACE = "namespace"
	DICT_KEY_IMPORT_LIST = "import_list"
	DICT_KEY_ANNOTATION_BLOCKS = "annotation_blocks"
	DICT_KEY_JSON_CLASSNAME = "json_classname"
	DICT_KEY_JSON_LIST = "json_list"
	DICT_KEY_PARAM_DICT = "param_dict"
	DICT_KEY_PARAM_LIST = "param_list"
	DICT_KEY_PARAM_TYPE = "param_type"
	DICT_KEY_PARAM_NAME = "param_name"
	DICT_KEY_PARAM_ISARRAY = "param_isarray"

	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, CFileReader.MODE_READ_CONTENT)
		self.m_info_dict = {}

	def full_content(self, content):
		# 获取所有的注释块
		self.m_info_dict[CJpParse.DICT_KEY_ANNOTATION_BLOCKS] = re.findall(r"\/\*(.*?)\*\/", content, re.S)

	def read_content(self, content, encoding):
		# 解析出 namespace 后的字符串
		namespace_list = re.findall(r".*?namespace (.*)?", content)
		length = len(namespace_list)
		namespace = ""
		if length == 0:
			# 使用文件名命名
			basename = os.path.basename(self.m_filepath)
			filename, ext = os.path.splitext(basename)
			namespace = filename
		elif length > 1:
			raise SystemExit("[Namespace Error] namespace too much")
		else:
			namespace = namespace_list[0]
		import_list = re.findall(r".*?import (.*)?", content)
		jpBlockList = re.findall(r"(?:^|[\s| ]+)json[ |\s]+?(.*?){(.*?)}", content, re.S)
		info_list = []
		for className, jpContent in jpBlockList:
			className = self.__del_white_char(className)
			jpContent = self.__del_white_char(jpContent)
			param_dict = self.__get_param_dict(jpContent)
			info_map = {}
			info_map[CJpParse.DICT_KEY_JSON_CLASSNAME] = className
			info_map[CJpParse.DICT_KEY_PARAM_DICT] = param_dict
			info_list.append(info_map)
		self.m_info_dict[CJpParse.DICT_KEY_NAMESPACE] = namespace
		self.m_info_dict[CJpParse.DICT_KEY_JSON_LIST] = info_list

	def __get_param_dict(self, content):
		param_dict = {}
		param_dict[CJpParse.DICT_KEY_PARAM_LIST] = self.__get_param_list(content)
		return param_dict

	def __get_param_list(self, content):
		ret_param_list = []
		param_list = content.split(",")
		for param_str in param_list:
			param_str = param_str.strip()
			if param_str == "":
				continue
			search = re.search(r"(.*?):(.*)?", param_str)
			gropus = search.groups()
			search_len = len(gropus)
			if search_len != 2:
				raise SystemExit("[Param Error] {0} (not exist ':' between param_name and param_type)".format(param_str))
			param_name = gropus[0]
			param_type = gropus[1]
			tmp_dict = {}
			is_array = False
			search = re.search(r".*?\[(.*?)\].*?", param_type)
			if search is not None:
				is_array = True
				param_type = search.groups()[0]
			param_name = re.sub(r"\"", "", param_name)
			tmp_dict[CJpParse.DICT_KEY_PARAM_TYPE] = param_type
			tmp_dict[CJpParse.DICT_KEY_PARAM_NAME] = param_name
			tmp_dict[CJpParse.DICT_KEY_PARAM_ISARRAY] = is_array
			ret_param_list.append(tmp_dict)
		return ret_param_list

	def __del_white_char(self, content):
		return re.sub(r"\s", "", content)

	def is_del_comment_annotation(self):
		return True

	def is_del_pound_annotation(self):
		return True

	def get_info_dict(self):
		return self.m_info_dict


if __name__ == "__main__":
	parser = CJpParse("../jp2gostruct/file/user_info.jp")
	parser.read()
	info_dict = parser.get_info_dict()
	print(info_dict)
