# encoding=utf8
import re
from file_handle_re import CFileReader


class ICppEnumParse(object):
	# [{key1: value1, key2: value2}, {...}]
	def parse_end(self, info_list):
		pass


class CCppEnumParse(CFileReader, ICppEnumParse):
    DICT_KEY_PRE_DECLARE = "pre_declare"
    DICT_KEY_BACK_DECLARE = "back_declare"
    DICT_KEY_ENUM_DICT = "enum_dict"
    DICT_KEY_ENUM_KEY = "enum_key"
    DICT_KEY_ENUM_VALUE = "enum_value"
    DICT_KEY_ENUM_PARAMS = "enum_params"
    DICT_KEY_PARAM_NAME = "param_name"
    DICT_KEY_PARAM_TYPE = "param_type"
    DICT_KEY_PARAM_ISARRAY = "param_isarray"
    DICT_KEY_PARAM_ISMUL = "param_ismul"
    DICT_KEY_FUNCTION_NAME = "func_name"
    __DICT_KEY_IS_MUL_PACK = "ismul"
    __DICT_KEY_FUNCTION_NAME = "function_name"

    def __init__(self, file_path):
        CFileReader.__init__(self, file_path, CFileReader.MODE_READ_CONTENT)
        self.m_info_list = []

    def read_content(self, content, encoding):
    	enumBlockList = re.findall(r"typedef enum(.*?){(.*?)}(.*?);", content, re.S)
    	for preDeclare, enumContent, backDeclare in enumBlockList:
    		# 过滤掉空白字符
    		text = self.__del_white_char(enumContent)
    		if text == "":
    			continue
    		enum_dict = self.__get_enum_dict(text)
    		pre = self.__del_white_char(preDeclare)
    		back = self.__del_white_char(backDeclare)
    		info_map = {}
    		info_map[CCppEnumParse.DICT_KEY_PRE_DECLARE] = pre
    		info_map[CCppEnumParse.DICT_KEY_BACK_DECLARE] = back
    		info_map[CCppEnumParse.DICT_KEY_ENUM_DICT] = enum_dict
    		self.m_info_list.append(info_map)
    	self.parse_end(self.m_info_list)

    def __get_enum_dict(self, content):
    	enum_dict = {}
    	list_tmp = content.split(",")
    	for item in list_tmp:
            # tmp = re.findall(r"\/\*(.*)?\*\/(.*?)=(.*)?", item)
    		# tuple_item = tuple(item.split("="))
    		# enum_list.append(tuple_item)
            eq_list = item.split("=")
            dict_tmp = {}
            length = len(eq_list)
            if length == 0:
                continue
            elif length == 1:
                dict_tmp[CCppEnumParse.DICT_KEY_ENUM_VALUE] = ""
            elif length == 2:
                dict_tmp[CCppEnumParse.DICT_KEY_ENUM_VALUE] = eq_list[1]
            # 获取注释列表
            anno_list = re.findall(r"\/\*(.*)?\*\/", eq_list[0])
            anno_length = len(anno_list)
            enum_k = re.sub(r"\/\*(.*)?\*\/", "", eq_list[0])
            if anno_length == 0:
                dict_tmp[CCppEnumParse.DICT_KEY_ENUM_PARAMS] = []
            else:
                # 获取距离最近的一个注释内容
                anno_content = anno_list[-1]
                obj_list = anno_content.split(";")
                tmp_list = []
                ismul = False
                function_name = ""
                for obj in obj_list:
                    split_list = obj.split(":")
                    if len(split_list) != 2:
                    	continue
                    k, v = split_list
                    if k == CCppEnumParse.__DICT_KEY_IS_MUL_PACK and v == "true":
                        ismul = True
                        continue
                    if k == CCppEnumParse.__DICT_KEY_IS_MUL_PACK:
                        continue
                    if k == CCppEnumParse.__DICT_KEY_FUNCTION_NAME:
                        function_name = v
                        continue
                    tmp = {}
                    tmp[CCppEnumParse.DICT_KEY_PARAM_NAME] = k
                    # 判断 v 中是否存在 [arr]
                    m = re.match(r".*?\[arr\].*?", v)
                    if m is None:
                        tmp[CCppEnumParse.DICT_KEY_PARAM_ISARRAY] = False
                    else:
                        tmp[CCppEnumParse.DICT_KEY_PARAM_ISARRAY] = True
                    v_tmp = re.sub(r"\[arr\]", "", v)
                    tmp[CCppEnumParse.DICT_KEY_PARAM_TYPE] = v_tmp
                    tmp_list.append(tmp)
                dict_tmp[CCppEnumParse.DICT_KEY_ENUM_PARAMS] = tmp_list
                dict_tmp[CCppEnumParse.DICT_KEY_PARAM_ISMUL] = ismul
                dict_tmp[CCppEnumParse.DICT_KEY_FUNCTION_NAME] = function_name
            dict_tmp[CCppEnumParse.DICT_KEY_ENUM_KEY] = enum_k
            enum_dict[enum_k] = dict_tmp
    	return enum_dict

    def __del_white_char(self, content):
    	return re.sub(r"\s", "", content)

    def is_del_comment_annotation(self):
        return True

    def is_del_pound_annotation(self):
        return True

    def get_info_list(self):
    	return self.m_info_list


if __name__ == "__main__":
    parse = CCppEnumParse("../client_sdk_script/file/cmpp_sdk.h")
    parse.read()
    result = parse.get_info_list()
    print(result)

