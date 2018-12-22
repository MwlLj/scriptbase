# encoding=utf8
import sys
import os
sys.path.append("../base/")
from string_tools import CStringTools
from file_handle_re import CFileHandle


class CWriteCppBase(object):
	def __init__(self, file_path):
		self.m_file_handler = CFileHandle()
		self.m_file_path = file_path

	def is_debug(self):
		return True

	def is_header(self):
		return True

	def define_name(self):
		# #ifndef xxx
		# #define xxx
		return ""

	def include_sys_list(self):
		# #include <xxx>
		return []

	def include_other_list(self):
		# #include "xxx"
		return []

	def namespace_list(self):
		# [(namespace1, [class1, class2]), (namespace2, [class1, class2])]
		return []

	def implement(self, namespace_name, class_name):
		return ""

	def namespace_implement_begin(self, namespace):
		return ""

	def namespace_implement_end(self, namespace):
		return ""

	def write(self, encoding="utf8"):
		content = ""
		if self.define_name() != "":
			content += self.write_header()
		sys_include_len = len(self.include_sys_list())
		other_include_len = len(self.include_other_list())
		include_count = sys_include_len + other_include_len
		if include_count > 0:
			content += self.write_includes()
		namespace_list_len = len(self.namespace_list())
		if namespace_list_len > 0:
			content += self.write_namespace()
		else:
			content += self.implement("", "")
		if self.define_name() != "":
			content += self.write_tail()
		if self.is_debug() is True:
			print(content)
		else:
			self.m_file_handler.clear_write(content, self.m_file_path, encoding)

	def write_member_var(self, param_type, param_name):
		content = ""
		param_type = self.type_change(param_type)
		content += "{0} {1};".format(param_type, param_name)
		return content

	def write_get_method(self, param_type, param_name):
		content = ""
		param_type = self.type_change(param_type)
		content += "const {0} &get{1}() const".format(param_type, CStringTools.upperFirstByte(param_name))
		content += " { return this->" + param_name + "; }"
		return content

	def write_set_method(self, param_type, param_name):
		content = ""
		param_type = self.type_change(param_type)
		content += "void set{0}(const {1} &{2})".format(CStringTools.upperFirstByte(param_name), param_type, param_name)
		content += " { this->" + "{0} = {0}".format(param_name) + "; }"
		return content

	def __write_construction_param(self, param_type, param_name):
		content = ""
		if param_type is None or param_name is None:
			return content
		param_type = self.type_change(param_type)
		content += "const {0} &{1}".format(param_type, param_name)
		return content

	def write_construction_param_list(self, param_list):
		content = ""
		length = len(param_list)
		i = 0
		for param_type, param_name in param_list:
			i += 1
			content += self.__write_construction_param(param_type, param_name)
			if i < length:
				content += ", "
		return content

	def write_default_init_param_list(self, param_list):
		return self.__write_init_param_list(param_list, True)

	def write_member_init_param_list(self, param_list):
		return self.__write_init_param_list(param_list, False)

	def __write_init_param(self, param_type, param_name, is_default):
		content = ""
		if param_type is None or param_name is None:
			return content
		param_type = self.type_change(param_type)
		value = param_name
		if param_type == "std::string":
			if is_default is True:
				value = '""'
		else:
			if is_default is True:
				value = "0"
		content += "{0}({1})".format(param_name, value)
		return content

	def __write_init_param_list(self, param_list, is_default):
		content = ""
		length = len(param_list)
		i = 0
		for param in param_list:
			if len(param) != 2:
				raise RuntimeError("param format error")
			i += 1
			param_type, param_name = param
			content += self.__write_init_param(param_type, param_name, is_default)
			if i < length:
				content += ", "
		return content

	def write_header(self):
		content = ""
		if self.is_header() is True:
			content += "#ifndef {0}\n".format(self.define_name())
			content += "#define {0}\n".format(self.define_name())
			content += "\n"
		return content

	def write_includes(self):
		content = ""
		for include in self.include_sys_list():
			content += '#include <{0}>\n'.format(include)
		for include in self.include_other_list():
			content += '#include "{0}"\n'.format(include)
		content += "\n"
		return content

	def write_namespace(self):
		content = ""
		namespaces = self.namespace_list()
		for np_name, class_list in namespaces:
			if np_name != "":
				content += "namespace {0}\n".format(np_name)
				content += "{\n\n"
			content += self.namespace_implement_begin(np_name)
			for class_name in class_list:
				if class_name == "":
					continue
				if self.is_header() is True:
					content += "class {0}\n".format(class_name)
					content += "{\n"
				content += self.implement(np_name, class_name)
				if self.is_header() is True:
					content += "};\n\n"
			if len(class_list) == 0:
				content += self.implement(np_name, "")
			content += self.namespace_implement_end(np_name)
			if np_name != "":
				content += "}\n\n"
		return content

	def write_tail(self):
		content = ""
		if self.is_header() is True:
			content += "#endif // {0}\n".format(self.define_name())
		return content

	def type_change(self, param_type):
		return param_type


class __CTest(CWriteCppBase):
	def __init__(self, file_path):
		CWriteCppBase.__init__(self, file_path)

	def define_name(self):
		# #ifndef xxx
		# #define xxx
		return "C_TEST"
		# return ""

	def include_sys_list(self):
		# #include <xxx>
		return ["string", "iostream"]

	def include_other_list(self):
		# #include "xxx"
		return ["test.h"]

	def namespace_list(self):
		# [(namespace1, [class1, class2]), (namespace2, [class1, class2])]
		return [("np1", ["class1", "class2"]), ("np2", ["class1"]), ("", ["CGlobClass1"])]

	def implement(self, namespace_name, class_name):
		return ""

	def is_header(self):
		return False

if __name__ == "__main__":
	test = __CTest("")
	test.write()
