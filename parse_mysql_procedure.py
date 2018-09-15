# encoding=utf8
import re
from file_handle_re import CFileReader


class CMysqlProcudureParse(CFileReader):
	DICT_KEY_NAMESPACE = "namespace"
	DICT_KEY_PROCEDURE_NAME = "procedure_name"
	DICT_KEY_PROCEDURE_LIST = "procedure_list"
	DICT_KEY_PROCEDURE_CONTENT = "procedure_content"
	DICT_KEY_PROCEDURE_FORMAT_PARAM_LIST = "format_param_list"
	DICT_KEY_PROCEDURE_INFO_DICT = "procedure_info_dict"
	DICT_KEY_PARAM_IN_ISMUL = "param_in_ismul"
	DICT_KEY_PARAM_OUT_ISMUL = "param_out_ismul"
	DICT_KEY_PARAM_LIST = "param_list"
	DICT_KEY_PARAM_INFO = "param_info"
	DICT_KEY_PARAM_MODE = "param_mode"
	DICT_KEY_PARAM_ISAUTO_INCREMENT = "param_isauto_increment"
	DICT_KEY_PARAM_TYPE = "param_type"
	DICT_KEY_PARAM_NAME = "param_name"
	DICT_KEY_PARAM_MODE_IN = "in"
	DICT_KEY_PARAM_MODE_OUT = "out"
	DICT_KEY_PARAM_MODE_IN_OUT = "in_out"
	__PARAM_MODE_IN_ISMUL = "in_isarr"
	__PARAM_MODE_OUT_ISMUL = "out_isarr"
	__PARAM_IS_AUTO_INCREMENT = "is_auto"

	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, CFileReader.MODE_READ_CONTENT)
		self.m_info_dict = {}

	def read_content(self, content, encoding):
		# 获取 namespace
		namespace = re.findall(r".*?#.*?namespace (.*)?", content)
		if len(namespace) == 0:
			raise RuntimeError("namespace is none")
		namespace = namespace[-1]
		# procedureList = re.findall(r".*?create .*?procedure (.*?)\((.*?)[\s|\)|^]begin[\s|$](.*?)[\s|^]end", content, re.S)
		procedureList = re.findall(r".*?create[\s|\n]+procedure[\s|\n]+(.*?)\((.*?)[\s|\)|^]begin[\s|$](.*?)[\s|^]end", content, re.S)
		procedure_list = []
		for procedure_name, format_param_list_str, procedure_content in procedureList:
			procedure_info_dict = {}
			procedure_name = self.__del_white_char(procedure_name)
			format_param_list_str = format_param_list_str.strip()
			procedure_content = procedure_content.strip()
			# 将 参数列表中最后一个 ) 去除
			if len(format_param_list_str) > 0:
				last_char = format_param_list_str[-1]
				if last_char == ')':
					format_param_list_str = format_param_list_str[:-1]
			# 获取存储过程传参中的参数列表
			format_param_list = self.__get_format_param_list(format_param_list_str)
			# 获取注释中的参数列表
			param_list_str = self.__get_recent_anno_param_str(content, procedure_name)
			in_ismul, out_ismul, param_list = self.__get_anno_param_list(param_list_str)
			procedure_info_dict[CMysqlProcudureParse.DICT_KEY_PROCEDURE_NAME] = procedure_name
			procedure_info_dict[CMysqlProcudureParse.DICT_KEY_PROCEDURE_FORMAT_PARAM_LIST] = format_param_list
			procedure_info_dict[CMysqlProcudureParse.DICT_KEY_PARAM_IN_ISMUL] = in_ismul
			procedure_info_dict[CMysqlProcudureParse.DICT_KEY_PARAM_OUT_ISMUL] = out_ismul
			procedure_info_dict[CMysqlProcudureParse.DICT_KEY_PARAM_LIST] = param_list
			procedure_info_dict[CMysqlProcudureParse.DICT_KEY_PROCEDURE_CONTENT] = procedure_content
			procedure_list.append(procedure_info_dict)
		self.m_info_dict[CMysqlProcudureParse.DICT_KEY_NAMESPACE] = namespace
		self.m_info_dict[CMysqlProcudureParse.DICT_KEY_PROCEDURE_LIST] = procedure_list

	def __get_format_param_list(self, param_list_str):
		param_list = []
		tmp_list = param_list_str.split(",")
		for item in tmp_list:
			param_dict = {}
			item = re.sub(r"\s{2,}", " ", item)
			# 去除空格中的空格
			item = re.sub(r"\(\s", "(", item)
			item = re.sub(r"\s\)", ")", item)
			item = item.strip()
			if item == "":
				continue
			infos = item.split(" ")
			length = len(infos)
			param_mode = ""
			param_name = ""
			param_type = ""
			if length == 2:
				# 既是输入也是输出
				param_mode = CMysqlProcudureParse.DICT_KEY_PARAM_MODE_IN_OUT
				param_name = infos[0]
				param_type = infos[1]
			elif length == 3:
				# 输入 / 输出
				param_mode, param_name, param_type = infos
			param_dict[CMysqlProcudureParse.DICT_KEY_PARAM_MODE] = param_mode
			param_dict[CMysqlProcudureParse.DICT_KEY_PARAM_NAME] = param_name
			param_dict[CMysqlProcudureParse.DICT_KEY_PARAM_TYPE] = param_type
			param_list.append(param_dict)
		return param_list

	def __get_anno_param_list(self, param_list_str):
		param_list_str = self.__del_white_char(param_list_str)
		param_list_split = param_list_str.split(";")
		in_ismul = False
		out_ismul = False
		param_list = []
		for param_info in param_list_split:
			param_dict = {}
			param_info_list = re.findall(r"\[(.*)?](.*)?:(.*)?", param_info)
			if len(param_info_list) < 1:
				continue
			param_ext, param_name, param_type = param_info_list[0]
			param_ext_list = param_ext.split("|")
			param_mode = param_ext_list[0]
			if param_mode == CMysqlProcudureParse.__PARAM_MODE_IN_ISMUL:
				if param_type == "true":
					in_ismul = True
				continue
			if param_mode == CMysqlProcudureParse.__PARAM_MODE_OUT_ISMUL:
				if param_type == "true":
					out_ismul = True
				continue
			is_auto = False
			# 获取是否是自增长的
			if len(param_ext_list) > 1:
				ext_match_result = re.match(r".*?{(.*)?}.*?", param_ext_list[-1])
				if ext_match_result is not None:
					match_str = ext_match_result.group(1)
					match_str = self.__del_white_char(match_str)
					match_list = match_str.split(",")
					for match in match_list:
						k_v = match.split(":")
						if len(k_v) == 1:
							raise RuntimeError("ext info error")
						k, v = k_v
						if k == CMysqlProcudureParse.__PARAM_IS_AUTO_INCREMENT and v == "true":
							is_auto = True
			param_dict[CMysqlProcudureParse.DICT_KEY_PARAM_MODE] = param_mode
			param_dict[CMysqlProcudureParse.DICT_KEY_PARAM_NAME] = param_name
			param_dict[CMysqlProcudureParse.DICT_KEY_PARAM_TYPE] = param_type
			param_dict[CMysqlProcudureParse.DICT_KEY_PARAM_ISAUTO_INCREMENT] = is_auto
			param_list.append(param_dict)
		return in_ismul, out_ismul, param_list

	def __get_recent_anno_param_str(self, content, procedure_name):
		# 获取最近的多行注释字符串
		lines = content.splitlines()
		anno_char_queue = []
		anno_buf = ""
		anno_str = ""
		for line in lines:
			queue_len = len(anno_char_queue)
			search1 = re.match(r".*?\/\*(.*)?", line)
			if search1 is not None:
				# 检测到 /* 填入临时队列
				anno_char_queue.append(0)
				anno_str = search1.groups()[0]
				anno_buf = ""
			search2 = re.match(r"(.*?)\*\/", line)
			if search2 is not None and queue_len > 0:
				anno_buf = anno_str + search2.groups()[0]
				anno_char_queue.clear()
				anno_str = ""
			if search1 is None and search2 is None and queue_len > 0:
				anno_str += line
			search = re.search(r".*?create[\s]+procedure[\s]+{0}.*?".format(procedure_name), line)
			if search is not None:
				break
		return anno_buf

	def __del_white_char(self, content):
		return re.sub(r"\s", "", content)

	def is_del_comment_annotation(self):
		return False

	def is_del_pound_annotation(self):
		return False

	def get_info_dict(self):
		return self.m_info_dict


if __name__ == "__main__":
	parser = CMysqlProcudureParse("../mysqlprocedure2cpp/file/user_info.sql")
	parser.read()
	info_dict = parser.get_info_dict()
	print(info_dict)
