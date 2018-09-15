# encoding=utf8
import os
import sys
import file_encoding
from get_file_info import CGetFileInfo
from get_md5 import CGetMd5


class IFileIsModify(object):
    def is_modify(self, filename):
        return False

    def is_compare_modify(self, filename1, filename2):
        return False


class CNotFileException(Exception):
    def __str__(self):
        return "path isn't file type"


class CTimeStampFileIsModify(IFileIsModify):
    m_file_recoder = {}

    def __init__(self):
        self.m_info_tool = CGetFileInfo()

    def is_modify(self, filename):
        try:
            # 判断是否是文件
            # if os.path.isfile(filename) is False:
            #     raise CNotFileException()
            timestamp = CTimeStampFileIsModify.m_file_recoder.get(filename)
            if timestamp is not None:
                # 已经存在了，先获取存在的时间戳，再比对当前的时间戳，返回比对结果
                cur_time_stamp = self.m_info_tool.get_modify_time(filename)
                if timestamp != cur_time_stamp:
                    CTimeStampFileIsModify.m_file_recoder[filename] = cur_time_stamp
                    return True
                else:
                    return False
            else:
                # 不存在，添加到字典中，并返回 False
                cur_time_stamp = self.m_info_tool.get_modify_time(filename)
                CTimeStampFileIsModify.m_file_recoder[filename] = cur_time_stamp
                return False
        except Exception as e:
            return False

    def is_compare_modify(self, filename1, filename2):
        try:
            file1_time = self.m_info_tool.get_modify_time(filename1)
            file2_time = self.m_info_tool.get_modify_time(filename2)
            if file1_time != file2_time:
                return True
            else:
                return False
        except Exception as e:
            return False


class CMd5FileIsModify(IFileIsModify):
    def __init__(self):
        self.m_md5 = CGetMd5()

    def is_modify(self, filename):
        return False

    def is_compare_modify(self, filename1, filename2):
        if os.path.exists(filename1) is False or os.path.exists(filename2) is False:
            return True
        fp1 = None
        fp2 = None
        try:
            encode1 = None
            encode2 = None
            try:
                encode1 = file_encoding.file_encoding(filename1)
                # 非二进制文件 -> 有 encoding 属性
                fp1 = open(filename1, "r", encoding=encode1)
            except Exception as e:
                # 二进制文件
                fp1 = open(filename1, "rb")
            try:
                encode2 = file_encoding.file_encoding(filename2)
                fp2 = open(filename2, "r", encoding=encode2)
            except Exception as e:
                fp2 = open(filename2, "rb")
            content1 = fp1.read()
            content2 = fp2.read()
            md1 = self.m_md5.calc_md5(content1)
            md2 = self.m_md5.calc_md5(content2)
            if md1 != md2:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
        finally:
            if fp1 is not None:
                fp1.close()
            if fp2 is not None:
                fp2.close()
