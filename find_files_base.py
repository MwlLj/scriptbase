# encoding=utf8
import os


class IFileClassify(object):
    def file_h(self, filename):
        pass

    def file_cpp(self, filename):
        pass

    def find_file(self, filepath):
        pass

    def find_dir(self, filepath):
        pass

    def find_end(self):
        pass


class CFileIteration(IFileClassify):
    def __init__(self, root_name, is_recursion=True):
        self.m_root = root_name
        self.m_is_recursion = is_recursion

    def __get_file_type(self, filename):
        list_tmp = filename.split('.')
        if len(list_tmp) < 2:
            return None
        return list_tmp[-1]

    def __find_dir(self, root):
        # 检测根目录是否是目录
        if os.path.isdir(root):
            self.find_dir(root)
            # 获取文件列表
            dir_list = os.listdir(root)
            for path in dir_list:
                full_path = root + "/" + path
                self.__find_dir(full_path)
            # 处理目录
            # self.__find_dir(root)
        elif os.path.isfile(root):
            # 处理文件
            self.__handle_file(root)

    def __find_file(self, root):
        # 检测根目录是否是目录
        if os.path.isdir(root):
            self.find_dir(root)
            # 获取文件列表
            dir_list = os.listdir(root)
            for path in dir_list:
                full_path = root + "/" + path
                if os.path.isfile(full_path):
                    self.__handle_file(full_path)
        elif os.path.isfile(root):
            # 处理文件
            self.__handle_file(root)

    def __handle_file(self, filename):
        str_file_type = self.__get_file_type(filename)
        if str_file_type is None:
            return
        if str_file_type == "h":
            self.file_h(filename)
        elif str_file_type == "cpp":
            self.file_cpp(filename)
        self.find_file(filename)

    def find(self):
        if self.m_is_recursion is True:
            self.__find_dir(self.m_root)
        else:
            self.__find_file(self.m_root)
        self.find_end()

