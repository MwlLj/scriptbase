# encoding=utf8
import time
import os
from threading import Thread
from file_is_modify import CTimeStampFileIsModify, CMd5FileIsModify


class IFileModifyCheck(Thread):
    def __init__(self):
        Thread.__init__(self)

    def start_check(self, files):
        pass

    def stop_check(self):
        pass

    def file_change(self, filename):
        pass


class AbstractFileModifyCheck(IFileModifyCheck):
    def __init__(self, interval_time):
        IFileModifyCheck.__init__(self)
        self.m_interval_time = interval_time
        self.m_is_stop = False
        # 源文件 - 目标路径
        self.m_file_mapping = {}

    def stop_check(self):
        self.m_is_stop = True

    def start_check(self, file_mapping):
        self.m_is_stop = False
        self.m_file_mapping = file_mapping
        self.start()


class CFileModifyCheck(AbstractFileModifyCheck):
    def __init__(self, interval_time=10):
        AbstractFileModifyCheck.__init__(self, interval_time)
        self.m_file_check = CTimeStampFileIsModify()

    def run(self):
        file_list = self.m_file_mapping.keys()
        while self.m_is_stop is False:
            time.sleep(self.m_interval_time)
            for filepath in file_list:
                if self.m_file_check.is_modify(filepath) is True:
                    self.file_change(filepath)


class CFileModifyCompareCheck(AbstractFileModifyCheck):
    def __init__(self, interval_time=10):
        AbstractFileModifyCheck.__init__(self, interval_time)
        self.m_file_check = CMd5FileIsModify()

    def run(self):
        while self.m_is_stop is False:
            time.sleep(self.m_interval_time)
            for src_path in self.m_file_mapping.keys():
                dst_paths = self.m_file_mapping[src_path]
                for dst_path in dst_paths:
                    if os.path.isdir(dst_path) is True:
                        filename = os.path.basename(src_path)
                        dst_path = dst_path + "/" + filename
                    elif os.path.isfile(dst_path) is True:
                        pass
                    if self.m_file_check.is_compare_modify(src_path, dst_path) is True:
                        self.file_change(src_path)


