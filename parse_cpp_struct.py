# encoding=utf8
import re
from file_handle_re import CFileReader


class CCppStructParse(CFileReader):
	DICT_KEY_PRE_DECLARE = "pre_declare"
	DICT_KEY_BACK_DECLARE = "back_declare"
	DICT_KEY_PARAM_DICT = "param_dict"
	DICT_KEY_PARAM_LIST = "param_list"
	DICT_KEY_PARAM_TYPE = "param_type"
	DICT_KEY_PARAM_NAME = "param_name"

	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, CFileReader.MODE_READ_CONTENT)
		self.m_info_list = []

	def read_content(self, content, encoding):
		structBlockList = re.findall(r".*?typedef .*?struct(.*?){(.*?)}(.*?);", content, re.S)
		for preDeclare, structContent, backDeclare in structBlockList:
			preDeclare = self.__del_white_char(preDeclare)
			backDeclare = self.__del_white_char(backDeclare)
			structContent = structContent.strip()
			param_dict = self.__get_param_dict(structContent)
			info_map = {}
			info_map[CCppStructParse.DICT_KEY_PRE_DECLARE] = preDeclare
			info_map[CCppStructParse.DICT_KEY_BACK_DECLARE] = backDeclare
			info_map[CCppStructParse.DICT_KEY_PARAM_DICT] = param_dict
			self.m_info_list.append(info_map)

	def __get_param_dict(self, content):
		param_dict = {}
		param_dict[CCppStructParse.DICT_KEY_PARAM_LIST] = self.__get_param_list(content)
		return param_dict

	def __get_param_list(self, content):
		ret_param_list = []
		param_list = content.split(";")
		for param_str in param_list:
			param_str = param_str.strip()
			if param_str == "":
				continue
			# 去除多余的空格
			param_str = re.sub("\s{2,}", " ", param_str)
			param_info = param_str.split(" ")
			param_info_len = len(param_info)
			if param_info_len != 2:
				continue
			tmp_dict = {}
			param_type, param_name = param_info
			tmp_dict[CCppStructParse.DICT_KEY_PARAM_TYPE] = param_type
			tmp_dict[CCppStructParse.DICT_KEY_PARAM_NAME] = param_name
			ret_param_list.append(tmp_dict)
		return ret_param_list

	def __del_white_char(self, content):
		return re.sub(r"\s", "", content)

	def is_del_comment_annotation(self):
		return True

	def is_del_pound_annotation(self):
		return True

	def get_info_list(self):
		return self.m_info_list


if __name__ == "__main__":
	parser = CCppStructParse("../struct2jp/file/twsp_sdk_struct.h")
	parser.read()
	info_list = parser.get_info_list()
	print(info_list)
	"""
	for item in info_list:
		back = item[CCppStructParse.DICT_KEY_BACK_DECLARE]
		if back == "T_TWSP_KEYBOARD_VIDEO_CHNINDEX_ALL_CHANGED_NTF":
			param_dict = item[CCppStructParse.DICT_KEY_PARAM_DICT]
			print(param_dict)
	"""
