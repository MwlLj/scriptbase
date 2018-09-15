# encoding=utf8
import sys
import os
sys.path.append("../base/")
from string_tools import CStringTools
from file_handle_re import CFileHandle


class CWriteCMakeListsBase(object):
	MODE_STATIC_LIB = 1
	MODE_DYNAMIC_LIB = 2
	MODE_EXECUTE = 3
	def __init__(self, file_path):
		self.m_file_handler = CFileHandle()
		self.m_file_path = file_path

	def is_debug(self):
		return True

	def mode(self):
		return CWriteCMakeListsBase.MODE_STATIC_LIB

	def include_paths(self):
		# include_directories(...)
		return []

	def header_list(self):
		# HEADER_LIST
		return []

	def link_lib_dirs(self):
		return []

	def win32_library_list(self):
		return []

	def linux_library_list(self):
		return []

	def obj_name(self):
		return ""

	def insert_after_include_dirs(self):
		return ""

	def insert_befor_if(self):
		return ""

	def write(self, encoding="utf8"):
		content = ""
		content += self.__write_include_dirs()
		if self.mode() == CWriteCMakeListsBase.MODE_EXECUTE:
			content += self.__write_link_lib_dirs()
		content += self.insert_after_include_dirs()
		content += self.__write_base_h_cpp()
		content += self.__write_add_header()
		if self.mode() == CWriteCMakeListsBase.MODE_EXECUTE:
			content += self.__write_add_execute()
			content += self.__write_set_target_properties()
		elif self.mode() == CWriteCMakeListsBase.MODE_STATIC_LIB:
			content += self.__write_add_library()
		content += self.insert_befor_if()
		if self.mode() == CWriteCMakeListsBase.MODE_EXECUTE:
			content += self.__write_target_link_libs()
		if self.is_debug() is True:
			print(content)
		else:
			self.m_file_handler.clear_write(content, self.m_file_path, encoding)

	def __write_include_dirs(self):
		content = ""
		content += "include_directories (\n"
		for d in self.include_paths():
			content += "\t"*1 + d
			content += "\n"
		content += ")\n"
		content += "\n"
		return content

	def __write_link_lib_dirs(self):
		content = ""
		content += "link_directories (\n"
		for lib in self.link_lib_dirs():
			content += "\t"*1 + lib
			content += "\n"
		content += ")\n"
		content += "\n"
		return content

	def __write_base_h_cpp(self):
		content = ""
		content += "aux_source_directory(source SOURCE_LIST)\n"
		content += 'FILE (GLOB HEADER_LIST "include/*.h")\n'
		content += "\n"
		return content

	def __write_add_header(self):
		content = ""
		content += "set (HEADER_LIST\n"
		content += "\t"*1 + "${HEADER_LIST}" + "\n"
		for h in self.header_list():
			content += "\t"*1 + h
			content += "\n"
		content += ")\n"
		content += "\n"
		return content

	def __write_add_library(self):
		content = ""
		content += "add_library (" + self.obj_name() + " STATIC ${SOURCE_LIST} ${HEADER_LIST})\n"
		content += "\n"
		return content

	def __write_add_execute(self):
		content = ""
		content += "add_executable (" + self.obj_name() + " ${SOURCE_LIST} ${HEADER_LIST})\n"
		content += "\n"
		return content

	def __write_set_target_properties(self):
		content = ""
		content += 'set_target_properties({0} PROPERTIES DEBUG_POSTFIX "_d")\n'.format(self.obj_name())
		content += "\n"
		return content

	def __write_target_link_libs(self):
		content = ""
		content += 'if (CMAKE_SYSTEM_NAME MATCHES "Windows")\n'
		content += "\t"*1 + "target_link_libraries ({0}\n".format(self.obj_name())
		for lib in self.win32_library_list():
			content += "\t"*2 + lib + "\n"
		content += "\t"*1 + ")\n"
		content += 'elseif (CMAKE_SYSTEM_NAME MATCHES "Linux")\n'
		content += "\t"*1 + "target_link_libraries ({0}\n".format(self.obj_name())
		for lib in self.linux_library_list():
			content += "\t"*2 + lib + "\n"
		content += "\t"*1 + ")\n"
		content += "\n"
		content += "\t"*1 + 'set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -static")\n'
		content += "\t"*1 + 'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static")\n'
		content += "\n"
		content += "\n"
		content += "\t"*1 + 'if (${CMAKE_BUILD_TYPE} STREQUAL "Release")\n'
		content += "\t"*2 + 'add_custom_command(TARGET '+ self.obj_name() +' POST_BUILD COMMAND echo "strip"\n'
		content += "\t"*4 + 'COMMAND ${STRIP} ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/'+ self.obj_name() + "\n"
		content += "\t"*4 + 'COMMAND cp ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/'+ self.obj_name() + ' ~/nfs/${PLATFORM_NAME} -f\n'
		content += "\t"*4 + ")\n"
		content += "\t"*1 + 'endif ()\n'
		content += "\n"
		content += "endif ()\n"
		return content


class __CTest(CWriteCMakeListsBase):
	def __init__(self, file_path):
		CWriteCMakeListsBase.__init__(self, file_path)

	def obj_name(self):
		return "test"


if __name__ == "__main__":
	test = __CTest("")
	test.write(encoding="utf8")
