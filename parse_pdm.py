# encoding=utf8
import re
from file_handle_re import CFileReader


class CPdmParse(CFileReader):
	ID = "id"
	OBJID = "objid"
	NAME = "name"
	CODE = "code"
	COMMENT = "comment"
	CREATOR = "creator"
	CREATE_TIME = "create_time"
	MODIFIER = "modifier"
	MODIFY_TIME = "modify_time"
	COLUMN_DATA_TYPE = "column_data_type"
	COLUMN_IDENTITY = "column_identity"
	COLUMN_MANDATORY = "column_mandatory"
	COLUMN_INFO_LIST = "column_info_list"
	PD_INFO_LIST = "pd_info_list"
	TABLE_INFO_LIST = "table_info_list"
	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, CFileReader.MODE_READ_CONTENT)
		self.m_info_dict = {}

	def read_content(self, content, encoding):
		pd_info_list = self.__get_physical_diagram_info_list(content)
		table_info_list = self.__get_table_info_list(content)
		self.m_info_dict[CPdmParse.PD_INFO_LIST] = pd_info_list
		self.m_info_dict[CPdmParse.TABLE_INFO_LIST] = table_info_list

	def __get_table_info_list(self, content):
		tables = self.__get_tag_content(r"c:Tables", content)
		table_list = re.findall(r"<o:Table(.*?)>(.*?)</o:Table>", tables, re.S)
		table_info_list = []
		for table in table_list:
			table_content, table_info = self.__get_tag_base_info(table)
			colums_info_list = self.__get_column_info_list(table_content)
			table_info[CPdmParse.COLUMN_INFO_LIST] = colums_info_list
			table_info_list.append(table_info)
		return table_info_list

	def __get_column_info_list(self, content):
		columns = self.__get_tag_content(r"c:Columns", content)
		column_list = re.findall(r"<o:Column(.*?)>(.*?)</o:Column>", columns, re.S)
		column_info_list = []
		for column in column_list:
			column_content, column_info = self.__get_tag_base_info(column)
			column_info = self.__get_column_ext_info(column_content, column_info)
			column_info_list.append(column_info)
		return column_info_list

	def __get_column_ext_info(self, content, column_info):
		data_type = self.__get_tag_content(r"a:DataType", content)
		column_mandatory = self.__get_tag_content(r"a:Column\.Mandatory", content)
		identity = self.__get_tag_content(r"a:Identity", content)
		column_info[CPdmParse.COLUMN_DATA_TYPE] = data_type
		column_info[CPdmParse.COLUMN_IDENTITY] = identity
		column_info[CPdmParse.COLUMN_MANDATORY] = column_mandatory
		return column_info

	def __get_physical_diagram_info_list(self, content):
		physical_diagrams = self.__get_tag_content(r"c:PhysicalDiagrams", content)
		physical_diagram_list = re.findall(r"<o:PhysicalDiagram(.*?)>(.*?)</o:PhysicalDiagram>.*?", self.__list2string(physical_diagrams), re.S)
		pd_info_list = []
		for pd in physical_diagram_list:
			pd_content, pd_info = self.__get_tag_base_info(pd)
			pd_info_list.append(pd_info)
		return pd_info_list

	def __get_tag_base_info(self, tag):
		tag_info = {}
		length = len(tag)
		tag_content = None
		tag_id = None
		if length == 1:
			tag_content = tag
		elif length == 2:
			tag_id_str, tag_content = tag
			tag_id = self.__get_tag_id(tag_id_str)
		else:
			return tag_content, tag_info
		tag_name = self.__get_tag_content(r"a:Name", tag_content)
		tag_code = self.__get_tag_content(r"a:Code", tag_content)
		tag_objid = self.__get_tag_content(r"a:ObjectID", tag_content)
		tag_creator = self.__get_tag_content(r"a:Creator", tag_content)
		tag_create_time = self.__get_tag_content(r"a:CreationDate", tag_content)
		tag_modifier = self.__get_tag_content(r"a:Modifier", tag_content)
		tag_modify_time = self.__get_tag_content(r"a:ModificationDate", tag_content)
		tag_comment = self.__get_tag_content(r"a:Comment", tag_content)
		tag_info[CPdmParse.ID] = tag_id
		tag_info[CPdmParse.NAME] = tag_name
		tag_info[CPdmParse.CODE] = tag_code
		tag_info[CPdmParse.OBJID] = tag_objid
		tag_info[CPdmParse.CREATOR] = tag_creator
		tag_info[CPdmParse.CREATE_TIME] = tag_create_time
		tag_info[CPdmParse.MODIFIER] = tag_modifier
		tag_info[CPdmParse.MODIFY_TIME] = tag_modify_time
		tag_info[CPdmParse.COMMENT] = tag_comment
		return tag_content, tag_info

	def __get_tag_id(self, content):
		search = re.search(r"(.*)?=(.*)?", content)
		tag_id = None
		if search is not None:
			groups = search.groups()
			tag_id = groups[1]
			tag_id = re.sub(r'"', "", tag_id)
		return tag_id

	def __get_tag_content(self, keyword, content):
		search = re.search(r"<{0}>(.*?)</{0}>".format(keyword), content, re.S)
		result = None
		if search is not None:
			groups = search.groups()
			result = groups[0]
		return result

	def __list2string(self, li):
		return "".join(li)

	def __del_white_char(self, content):
		return re.sub(r"\s", "", content)

	def is_del_comment_annotation(self):
		return False

	def is_del_pound_annotation(self):
		return False

	def get_info_dict(self):
		return self.m_info_dict


if __name__ == "__main__":
	parser = CPdmParse("../pdm2sql/file/iacdevdb.pdm")
	parser.read()
	info_dict = parser.get_info_dict()
	print(info_dict)
