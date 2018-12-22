# encoding=utf8
import re
from file_handle_re import CFileReader


class CGoStructParse(CFileReader):
	PACKAGE = "package"
	STRUCT_LIST = "struct_list"
	STRUCT_NAME = "struct_name"
	PARAM_LIST = "param_list"
	PARAM_TYPE = "param_type"
	PARAM_NAME = "param_name"
	REFLEX_CONTENT = "reflex_content"

	def __init__(self, file_path):
		CFileReader.__init__(self, file_path, CFileReader.MODE_READ_CONTENT)
		self.m_info_dict = {}

	def read_content(self, content, encoding):
		# 获取 package
		package = re.findall(r"(?:^|[\s]*?)package[ ]+?(.*)?", content)
		if len(package) == 0:
			raise RuntimeError("package is none")
		package = package[-1]
		struct_infos = re.findall(r"type[ ]+?(.*?)[ ]+?struct[\s]*?{[\s]*?(.*?)}", content, re.S)
		struct_list = []
		for struct_info in struct_infos:
			info = {}
			if len(struct_info) != 2:
				raise SystemExit("[ERROR] struct error")
			param_list = []
			struct_name, struct_body = struct_info
			struct_body = struct_body.strip()
			bodys = struct_body.splitlines()
			for body in bodys:
				param = {}
				body = body.strip()
				# parse name type ``
				results = re.findall(r"(.*?)[ ]+?(.*?)[ ]+?`(.*?)`", body)
				if len(results) == 0:
					results = re.findall(r"(.*?)[ ]+?(.*)?", body)
					if len(results) == 0:
						continue
				result = results[0]
				values_len = len(result)
				if values_len < 2 or values_len > 3:
					raise SystemExit("[ERROR] sturct {0}: field error".format(struct_name))
				param_name = None
				param_type = None
				reflex_content = None
				if values_len == 2:
					param_name, param_type = result
				else:
					param_name, param_type, reflex_content = result
				param[CGoStructParse.PARAM_NAME] = param_name
				param[CGoStructParse.PARAM_TYPE] = param_type
				param[CGoStructParse.REFLEX_CONTENT] = reflex_content
				param_list.append(param)
			info[CGoStructParse.STRUCT_NAME] = struct_name
			info[CGoStructParse.PARAM_LIST] = param_list
			struct_list.append(info)
		self.m_info_dict[CGoStructParse.PACKAGE] = package
		self.m_info_dict[CGoStructParse.STRUCT_LIST] = struct_list

	def __mul_space_to_single(self, body):
		return re.sub(r"[ ]+", " ", body)

	def __del_white_char(self, content):
		return re.sub(r"\s", "", content)

	def is_del_comment_annotation(self):
		return True

	def is_del_pound_annotation(self):
		return True

	def get_info_dict(self):
		return self.m_info_dict


if __name__ == "__main__":
	parser = CGoStructParse("../struct2cpp/example_struct/test.struct")
	parser.read()
	info_dict = parser.get_info_dict()
	print(info_dict)
