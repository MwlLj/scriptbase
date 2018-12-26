# encoding=utf8
import re
from file_handle_re import CFileReader


class CSqlParse(CFileReader):
	NAMESPACE = "namespace"
	CREATE_TABELS_SQL = "create_tables_sql"
	CREATE_TABLE_LIST = "create_table_list"
	CREATE_FUNCTION_SQLS = "create_function_sqls"
	IMPORT_LIST = "import_list"
	METHOD_LIST = "method_list"
	FUNC_NAME = "func_name"
	BREF = "bref"
	IN_CLASS = "in_class"
	OUT_CLASS = "out_class"
	BUFLEN = "buf_len"
	IN_ISARR = "in_isarr"
	OUT_ISARR = "out_isarr"
	IS_BRACE = "is_brace"
	HAS_RES = "has_res"
	IS_GROUP = "is_group"
	GROUP_INPUT_PARAMS = "group_input_params"
	SQL_GROUP_LIST = "sql_group_list"
	SQL_GROUP_INFO = "sql_group_info"
	INPUT_PARAMS = "input_params"
	OUTPUT_PARAMS = "output_params"
	PARAM_TYPE = "param_type"
	PARAM_NAME = "param_name"
	PARAM_IS_CONDITION = "param_is_condition"
	SQL = "sql"
	__CONDITION = "[cond]"
	__KEYWORD_BREF = "@bref"
	__KEYWORD_BUFLEN = "@buf_len"
	__KEYWORD_IN_CLASS = "@in_class"
	__KEYWORD_OUT_CLASS = "@out_class"
	__KEYWORD_IN_ISARR = "@in_isarr"
	__KEYWORD_OUT_ISARR = "@out_isarr"
	__KEYWORD_GROUPIN = "@gin"
	__KEYWORD_IN = "@in"
	__KEYWORD_OUT = "@out"
	__KEYWORD_ISBRACE = "@is_brace"
	__KEYWORD_ISGROUP = "@is_group"
	__KEYWORD_HAS_RES = "@has_res"

	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, CFileReader.MODE_READ_CONTENT)
		self.m_info_dict = {}

	def read_content(self, content, encoding):
		# 获取 namespace
		namespace = re.findall(r"(?:^|[\s]*?)#[ ]*?namespace[ ]+?(.*)?", content)
		if len(namespace) == 0:
			raise RuntimeError("namespace is none")
		namespace = namespace[-1]
		# 获取创建表的 sql
		create_table_list = []
		create_tables_sql = ""
		create_tables = re.findall(r"(?:^|[\s]*?)#create[ ]+?tables[\s]*?\/\*(.*?)\*\/[\s]*?#end", content, re.S)
		for create_table in create_tables:
			after_handle_sql = self.del_annotation(create_table)
			create_tables_sql += after_handle_sql
			create_table_list.append(self.__filter_sql(after_handle_sql))
		create_tables_sql = self.__filter_sql(create_tables_sql)
		create_functions = re.findall(r"(?:^|[\s]*?)#create[ ]+?function[\s]*?\/\*(.*?)\*\/[\s]*?#end", content, re.S)
		# 获取import路径列表
		import_list = re.findall(r"(?:^|[\s]*?)#[ ]*?import[ ]+?(.*)?", content)
		# 获取 注释体 和 语句体
		method_list = []
		find_result = re.findall(r"\/\*(.*?)\*\/[\s]*?#define[ ]+?(.*?)[\s]+?(.*?)#end", content, re.S)
		for result in find_result:
			if len(result) != 3:
				continue
			anno_block, func_name, sql_str = result
			if func_name == "":
				continue
			bref, buf_len, is_brace, has_res, is_group, in_class, out_class, in_isarr, out_isarr, group_input_params, input_params, output_params = self.__parse_anno_block(anno_block)
			sql_info = self.__parse_sql(sql_str)
			sql_str = self.__filter_sql(sql_str)
			method_info = {}
			method_info[CSqlParse.FUNC_NAME] = func_name
			method_info[CSqlParse.SQL] = sql_str
			method_info[CSqlParse.SQL_GROUP_INFO] = sql_info
			if bref is not None:
				method_info[CSqlParse.BREF] = bref
			if buf_len is not None:
				method_info[CSqlParse.BUFLEN] = buf_len
			if is_brace is not None:
				if is_brace.lower() == "true":
					is_brace = True
				elif is_brace.lower() == "false":
					is_brace = False
				else:
					is_brace = None
				method_info[CSqlParse.IS_BRACE] = is_brace
			if has_res is not None:
				if has_res.lower() == "true":
					has_res = True
				elif has_res.lower() == "false":
					has_res = False
				else:
					has_res = None
				method_info[CSqlParse.HAS_RES] = has_res
			if is_group is not None:
				if is_group.lower() == "true":
					is_group = True
				elif is_group.lower() == "false":
					is_group = False
				else:
					is_group = None
				method_info[CSqlParse.IS_GROUP] = is_group
			if in_class is not None:
				method_info[CSqlParse.IN_CLASS] = in_class
			if out_class is not None:
				method_info[CSqlParse.OUT_CLASS] = out_class
			if in_isarr is not None:
				method_info[CSqlParse.IN_ISARR] = in_isarr
			if out_isarr is not None:
				method_info[CSqlParse.OUT_ISARR] = out_isarr
			if group_input_params is not None:
				method_info[CSqlParse.GROUP_INPUT_PARAMS] = group_input_params
			if input_params is not None:
				method_info[CSqlParse.INPUT_PARAMS] = input_params
			if output_params is not None:
				method_info[CSqlParse.OUTPUT_PARAMS] = output_params
			method_list.append(method_info)
		self.m_info_dict[CSqlParse.NAMESPACE] = namespace
		self.m_info_dict[CSqlParse.CREATE_TABELS_SQL] = create_tables_sql
		self.m_info_dict[CSqlParse.CREATE_TABLE_LIST] = create_table_list
		self.m_info_dict[CSqlParse.CREATE_FUNCTION_SQLS] = create_functions
		self.m_info_dict[CSqlParse.IMPORT_LIST] = import_list
		self.m_info_dict[CSqlParse.METHOD_LIST] = method_list

	def __parse_anno_block(self, anno_block):
		bref = None
		buf_len = None
		in_class = None
		out_class = None
		in_isarr = None
		out_isarr = None
		is_brace = None
		has_res = None
		is_group = None
		group_input_params = []
		input_params = []
		output_params = []
		lines = anno_block.splitlines()
		for line in lines:
			if line == "":
				continue
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_BREF, line)
			if is_keyword is not None:
				bref = is_keyword
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_BUFLEN, line)
			if is_keyword is not None:
				buf_len = self.__del_white_char(is_keyword)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_ISBRACE, line)
			if is_keyword is not None:
				is_brace = self.__del_white_char(is_keyword)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_HAS_RES, line)
			if is_keyword is not None:
				has_res = self.__del_white_char(is_keyword)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_ISGROUP, line)
			if is_keyword is not None:
				is_group = self.__del_white_char(is_keyword)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_IN_CLASS, line)
			if is_keyword is not None:
				in_class = self.__del_white_char(is_keyword)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_OUT_CLASS, line)
			if is_keyword is not None:
				out_class = self.__del_white_char(is_keyword)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_IN_ISARR, line)
			if is_keyword is not None:
				in_isarr = self.__del_white_char(is_keyword)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_OUT_ISARR, line)
			if is_keyword is not None:
				out_isarr = self.__del_white_char(is_keyword)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_GROUPIN, line)
			if is_keyword is not None:
				tmp = self.__parse_param_str(is_keyword)
				if tmp is not None:
					input_params.append(tmp)
					group_input_params.append(tmp)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_IN, line)
			if is_keyword is not None:
				tmp = self.__parse_param_str(is_keyword)
				if tmp is not None:
					input_params.append(tmp)
			is_keyword = self.__is_keyword(CSqlParse.__KEYWORD_OUT, line)
			if is_keyword is not None:
				tmp = self.__parse_param_str(is_keyword)
				if tmp is not None:
					output_params.append(tmp)
		if len(input_params) == 0:
			input_params = None
		if len(output_params) == 0:
			output_params = None
		if len(group_input_params) == 0:
			group_input_params = None
		return bref, buf_len, is_brace, has_res, is_group, in_class, out_class, in_isarr, out_isarr, group_input_params, input_params, output_params

	def __parse_sql(self, sql_str):
		sql_info = {}
		"""
		sql_list = sql_str.split(";")
		sql_list = sql_list[:-1]
		group_list = []
		for sql in sql_list:
			group_field_list = re.findall(r"\/\*begin\*\/(.*?)\/\*end\*\/", sql, re.S)
			group_list.append(group_field_list)
		"""
		group_field_list = re.findall(r"\/\*begin\{(.*?)\}\*\/(.*?)\/\*end\*\/", sql_str, re.S)
		tmp = []
		for g in group_field_list:
			if len(g) != 2:
				raise SystemExit("[Number Not Found]" + sql_str)
			no, field = g
			field = field.strip()
			tmp.append((no, field))
		sql_info[CSqlParse.SQL_GROUP_LIST] = tmp
		return sql_info

	def __parse_param_str(self, param_str):
		search = re.search(r"(.*?):(.*)?", param_str)
		groups = search.groups()
		search_len = len(groups)
		if search_len != 2:
			raise SystemExit("[Param Error] {0} (not exist ':' between param_name and param_type)".format(param_str))
		param_name = groups[0]
		is_cond = False
		if CSqlParse.__CONDITION in param_name:
			param_name = re.sub(r"\[.*?\]", "", param_name)
			is_cond = True
		tmp = {}
		tmp[CSqlParse.PARAM_NAME] = self.__del_white_char(param_name)
		tmp[CSqlParse.PARAM_TYPE] = self.__del_white_char(groups[1])
		tmp[CSqlParse.PARAM_IS_CONDITION] = is_cond
		return tmp

	def __filter_sql(self, sql_str):
		sql = ""
		lines = sql_str.splitlines()
		length = len(lines)
		i = 0
		for line in lines:
			i += 1
			if line == "":
				continue
			line = re.sub(r'"', '\\"', line)
			sql += line
			if i < length:
				sql += "\\" + "\n"
		return sql

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
	parser = CSqlParse("../sqlitesql2cpp/example_sql/user_info.sql")
	parser.read()
	info_dict = parser.get_info_dict()
	print(info_dict)
