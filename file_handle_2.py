# encoding=utf8
import os
import sys
import re
import shutil


class CFileNotExistExcept(Exception):
    def __str__(self):
        return "path is not exist"


class CFileHandle(object):
    def __init__(self):
        pass

    def read_line(self, content, encoding):
        pass

    def read_end(self):
        pass

    def is_del_mulline_annotation(self):
        return False

    def copy(self, src_file_path, dst_path):
        try:
            # 判断目标是文件还是目录
            if os.path.isfile(dst_path):
                shutil.copyfile(src_file_path, dst_path)
            elif os.path.isdir(dst_path):
                filename = os.path.basename(src_file_path)
                dst_file_path = dst_path + "/" + filename
                shutil.copyfile(src_file_path, dst_file_path)
            # 判断文件是否存在
            if os.path.exists(dst_path) is False:
                raise CFileNotExistExcept()
        except Exception as e:
            print(e)


class CFileReader(CFileHandle):
    def __init__(self, file_path):
        self.m_mul_annotation_queue = []
        self.m_filepath = file_path
        self.m_fp = None

    def __is_start_mul_annotation(self):
        if len(self.m_mul_annotation_queue) == 0:
            return False
        tmp = self.m_mul_annotation_queue[-1]
        if tmp == "/*":
            return True
        else:
            return False

    def __is_end_mul_annotation(self):
        if len(self.m_mul_annotation_queue) == 0:
            return True
        tmp = self.m_mul_annotation_queue[-1]
        if tmp == "*/":
            return True
        else:
            return False

    def __push_symbol_to_mul_annotation(self, symbol):
        self.m_mul_annotation_queue.append(symbol)

    def __del_mul_annotation(self, content, encoding):
        content = re.sub(r"#.*", "", content)
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"/\*.*?\*/", "", content)
        if "/*" in content and self.__is_end_mul_annotation() is True:
            self.__push_symbol_to_mul_annotation("/*")
            result = re.match(r"(.*?)/\*", content)
            result = result.group().replace("/*", "")
            self.read_line(result, encoding)
            self.m_is_mul_annotation = True
            content = re.sub(r"/\*.*?$", "", content)
        if "*/" in content and self.__is_start_mul_annotation() is True:
            self.__push_symbol_to_mul_annotation("*/")
            result = re.match(r".*?\*/(.*?)$", content)
            result = result.group()
            content = re.sub(r"^.*?\*/", "", result)
            if "/*" in content:
                # print(content)
                self.__push_symbol_to_mul_annotation("/*")
                self.__del_mul_annotation(content, encoding)
            # print(content)
            # content = re.sub(r"/\*.*?\*/", "", content)
        if self.__is_end_mul_annotation() is True:
            # print(content)
            self.read_line(content, encoding)

    def read(self):
        try:
            encoding = "utf-8"
            self.m_fp = open(self.m_filepath, "r", encoding=encoding)
            while True:
                line = self.m_fp.readline()
                if line == "":
                    break
                if self.is_del_mulline_annotation() is True:
                    self.__del_mul_annotation(line, encoding)
                else:
                    self.read_line(line, encoding)
        except Exception as e:
            print(e)
        finally:
            if self.m_fp is not None:
                self.m_fp.close()
        self.m_mul_annotation_queue.clear()
        self.read_end()


if __name__ == "__main__":
    file_handle = CFileHandle()
    file_handle.copy("__init__.py", "../test")


