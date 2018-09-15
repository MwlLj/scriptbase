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
        self.m_is_mul_annotation = False
        self.m_filepath = file_path
        self.m_fp = None

    def __del_mul_annotation(self, content, encoding):
        content = re.sub(r"/\*.*?\*/", "", content)
        if "/*" in content and self.m_is_mul_annotation is False:
            result = re.match(r"(.*?)/\*", content)
            result = result.group().replace("/*", "")
            self.read_line(result, encoding)
            self.m_is_mul_annotation = True
            content = re.sub(r"/\*.*?$", "", content)
        if "*/" in content and self.m_is_mul_annotation is True:
            result = re.match(r".*?\*/(.*?)$", content)
            result = result.group()
            self.m_is_mul_annotation = False
            # print(result)
            # self.m_is_mul_annotation = False
            content = re.sub(r"^.*?\*/", "", result)
            if "/*" in content:
                print(content)
                self.m_is_mul_annotation = False
                self.__del_mul_annotation(content, encoding)
                self.m_is_mul_annotation = False
            # print(content)
            # content = re.sub(r"/\*.*?\*/", "", content)
        if self.m_is_mul_annotation is False:
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
        self.read_end()


if __name__ == "__main__":
    file_handle = CFileHandle()
    file_handle.copy("__init__.py", "../test")


