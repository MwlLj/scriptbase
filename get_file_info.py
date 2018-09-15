# encoding=utf8
import os
import time


class IGetFileInfo(object):
    def get_modify_time(self, filename):
        pass

    def get_create_time(self, filename):
        pass

    def get_access_time(self, filename):
        pass

    def get_file_size(self, filename):
        pass

    def timestamp_to_time(self, timestamp):
        time_struct = time.localtime(timestamp)
        return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)


class CGetFileInfo(IGetFileInfo):
    def get_access_time(self, filename):
        # 转换文件路径
        filename = filename.encode("utf8")
        t = os.path.getatime(filename)
        return self.timestamp_to_time(t)

    def get_modify_time(self, filename):
        filename = filename.encode("utf8")
        if os.path.exists(filename) is False:
            return ""
        t = os.path.getmtime(filename)
        return self.timestamp_to_time(t)

    def get_create_time(self, filename):
        filename = filename.encode("utf8")
        t = os.path.getctime(filename)
        return self.timestamp_to_time(t)

    def get_file_size(self, filename):
        filename = filename.encode("utf8")
        size = os.path.getsize(filename)
        size = size / float(1024 * 1024)

        return round(size, 2)


