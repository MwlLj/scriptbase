# encoding=utf8
import os
import sys
import re
import shutil
import file_encoding


class CFileNotExistExcept(Exception):
    def __str__(self):
        return "path is not exist"


class CFileHandle(object):
    def __init__(self):
        pass

    def read_line(self, content, encoding):
        pass

    def read_content(self, content, encoding):
        pass

    def read_end(self):
        pass

    def full_content(self, content):
        pass

    def is_del_mulline_annotation(self):
        return False

    def is_del_comment_annotation(self):
        return False

    def is_del_pound_annotation(self):
        return False

    def is_del_mul_annotation(self):
        return False

    def copy(self, src_file_path, dst_path):
        try:
            # 判断文件是否存在
            if os.path.exists(dst_path) is False:
                raise CFileNotExistExcept()
            # 判断目标是文件还是目录
            if os.path.isfile(dst_path):
                shutil.copyfile(src_file_path, dst_path)
            elif os.path.isdir(dst_path):
                filename = os.path.basename(src_file_path)
                dst_file_path = dst_path + "/" + filename
                shutil.copyfile(src_file_path, dst_file_path)
        except Exception as e:
            print(e)

    def clear_write(self, content, dst_path, encoding):
        fp = None
        try:
            try:
                fp = open(dst_path, "w+", encoding=encoding)
            except Exception as e:
                fp = open(dst_path, "w+")
            else:
                pass
            finally:
                pass
            fp.write(content)
        except Exception as e:
            print(e)
        finally:
            if fp is not None:
                fp.close()

    def create_file(self, path):
        fp = None
        try:
            fp = open(dst_path, "w")
        except Exception as e:
            print(e)
        finally:
            if fp is not None:
                fp.close()


class CFileReader(CFileHandle):
    MODE_READ_LINE = 1
    MODE_COMMA_SPLIT = 2
    MODE_READ_CONTENT = 3

    def __init__(self, file_path, line_mode=MODE_READ_LINE):
        self.m_filepath = file_path
        self.line_mode = line_mode
        self.m_full_content = ""
        self.m_fp = None

    def set_root_path(self, path):
        self.m_filepath = path

    def get_file_path(self):
        return self.m_filepath

    def __del_mulline_annotation(self, content, encoding):
        content = re.sub(r"#.*", "", content)
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"(\/\*(\s|.)*?\*\/)", "", content)
        return content

    def __del_comment_annotation(self, content):
        content = re.sub(r"//.*", "", content)
        return content

    def __del_pound_annotation(self, content):
        content = re.sub(r"#.*", "", content)
        return content

    def __del_mul_annotation(self, content):
        content = re.sub(r"(\/\*(\s|.)*?\*\/)", "", content)
        return content

    def get_content(self):
        return self.m_full_content

    def read(self):
        try:
            # encoding = "utf-8"
            encoding = file_encoding.file_encoding(self.m_filepath)
            try:
                self.m_fp = open(self.m_filepath, "r", encoding=encoding)
            except Exception as e:
                self.m_fp = open(self.m_filepath, "r")
            else:
                pass
            finally:
                pass
            content = self.m_fp.read()
            self.m_full_content = content
            self.full_content(content)
            if self.is_del_mulline_annotation() is True:
                content = self.__del_mulline_annotation(content, encoding)
            if self.is_del_mul_annotation() is True:
                content = self.__del_mul_annotation(content)
            if self.is_del_comment_annotation() is True:
                content = self.__del_comment_annotation(content)
            if self.is_del_pound_annotation() is True:
                content = self.__del_pound_annotation(content)
            if self.line_mode == CFileReader.MODE_READ_LINE:
                lines = content.splitlines()
            elif self.line_mode == CFileReader.MODE_COMMA_SPLIT:
                content = re.sub(r"\s", "", content)
                content = content.replace(" ", "")
                lines = content.split(";")
            elif self.line_mode == CFileReader.MODE_READ_CONTENT:
                self.read_content(content, encoding)
                return
            for line in lines:
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


