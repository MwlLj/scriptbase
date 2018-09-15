# encoding=utf8
import sys
import encodings
import re
import file_encoding


class IKeywordFilter(object):
    def filter(self, content):
        return content

class CStdCppKeywordFilter(IKeywordFilter):
    def filter(self, content):
        content = re.sub(r"(public[ ]*:|private[ ]*:|protected[ ]*:|virtual|explicit)", "", content)
        return content

class CQtKeywordFilter(IKeywordFilter):
    def filter(self, content):
        content = re.sub(r"(public[ ]*slots[ ]*:|private[ ]*slots[ ]*:|protected[ ]*slots[ ]*:|signals[ ]*:|Q_OBJECT|)", "", content)
        return content


class ICppHeadFileParse(object):
    def parse(self, file_path):
        pass

    def parse_finish(self, info_list):
        pass


class CCppHeadFileParse(ICppHeadFileParse):
    CLASS_NAME = "class_name"
    PARENTS = "parents"
    PARENT_NAME = "parent_name"
    CLASS_PROPERTY = "class_property"
    METHOD_DEFINE_BODY = "method_define_body"
    METHOD_RETURN_TYPE = "method_return_type"
    METHOD_NAME = "method_name"
    IS_VIRTUAL_METHOD = "is_virtual_method"
    METHOD_PARAM_LIST = "method_param_list"
    METHOD_PARAM_TYPE = "method_param_type"
    METHOD_PARAM_NAME = "method_param_name"
    INIT_PARAM_LIST = "init_param_list"
    INIT_PARAM_NAME = "init_param_name"
    INIT_PARAM_VALUE = "init_param_value"

    def __init__(self):
        self.m_std_cpp_keyword_filter = CStdCppKeywordFilter()
        self.m_qt_keyword_filter = CQtKeywordFilter()

    def parse(self, file_path):
        fp = None
        info_list = []
        try:
            file_encode = file_encoding.file_encoding(file_path)
            fp = open(file_path, "r", encoding=file_encode)
            content = fp.read()
            info_list = self.__parse(content)
        except Exception as e:
            print(e)
        finally:
            if fp is not None:
                fp.close()
        self.parse_finish(info_list)

    def __parse(self, content):
        content = self.__del_annotate(content)
        class_info_list = self.__get_class_info(content)
        return class_info_list

    def __get_class_info(self, content):
        # content = content.replace("\n", "").replace("\r", "")
        match_result = re.findall(r"class([^;]*?){(.*?)}[ ]*;", content, re.S)
        class_info_list = []
        for result in match_result:
            first, second = result
            # 处理class到{之前的数据
            first_result = self.__handle_first(first)
            # 处理{}中的数据
            second_result = self.__handle_second(second)
            class_info_list.append((first_result, second_result))
        return class_info_list

    def __del_blank_char(self, content):
        content = re.sub(r"[\f\n\r\t\v]", "", content)
        # content = re.sub(r"\s+", "", content)
        return content

    def __del_blank_char_and_space(self, content):
        content = re.sub(r"\s+", "", content)
        return content

    def __handle_first(self, content):
        first_result = {}
        content = self.__del_blank_char(content)
        tmp_list = content.split(":")
        if len(tmp_list) == 0:
            return first_result
        elif len(tmp_list) == 1:
            first_result[CCppHeadFileParse.CLASS_NAME] = tmp_list[0].strip()
            first_result[CCppHeadFileParse.PARENTS] = None
        elif len(tmp_list) == 2:
            first_result[CCppHeadFileParse.CLASS_NAME] = tmp_list[0].strip()
            # 以逗号分割, 获取每一个基类
            parent_list_tmp = tmp_list[1].split(",")
            parent_info_list = []
            for parent_tmp in parent_list_tmp:
                dict_tmp = {}
                parent_tmp = self.__del_blank_char(parent_tmp)
                li_tmp = parent_tmp.strip().split(" ")
                if len(li_tmp) != 2:
                    continue
                dict_tmp[CCppHeadFileParse.CLASS_PROPERTY] = li_tmp[0]
                dict_tmp[CCppHeadFileParse.PARENT_NAME] = li_tmp[1]
                parent_info_list.append(dict_tmp)
            first_result[CCppHeadFileParse.PARENTS] = parent_info_list
        return first_result

    def __handle_second(self, content):
        second_result = []
        content = self.m_std_cpp_keyword_filter.filter(content)
        content = self.m_qt_keyword_filter.filter(content)
        content = self.__del_blank_char(content)
        # 获取头文件中定义的方法
        match_result = re.findall(r".*?{[^{]*}", content)
        for result in match_result:
            dict_tmp = {}
            # 获取方法名称
            mt = re.match(r"(.*?){", result)
            mt_gp = mt.group()
            method_text = mt_gp.replace("{", "")
            dict_tmp = self.__get_method_info_include_init_param_list(method_text, dict_tmp)
            # 获取头文件定义中的文本
            mt = re.search(r"{.*}", result)
            mt_gp = mt.group()
            print(mt_gp)
            dict_tmp[CCppHeadFileParse.METHOD_DEFINE_BODY] = mt_gp
            second_result.append(dict_tmp)
        # 删除头文件中定义的方法
        content = re.sub(r".*?{[^{]*}", "", content)
        method_list = content.split(";")
        for method_text in method_list:
            dict_tmp = {}
            dict_tmp = self.__get_method_info(method_text, dict_tmp)
            second_result.append(dict_tmp)
        return second_result

    def __get_method_info_include_init_param_list(self, content, info_dict):
        content = content.strip()
        # 先判断是否存在初始化参数列表
        # list_tmp = content.split(":")
        match_result = re.match(r"(.*?):", content)
        if match_result is not None:
            gp = match_result.group()
            init_text = content.replace(gp, "")
            # 获取初始化参数列表
            init_param_list = init_text.split(",")
            param_list = []
            for param_text in init_param_list:
                dict_tmp = {}
                # 获取括号中的值
                search_result = re.search(r"\(.*\)", param_text)
                if search_result is None:
                    continue
                gt_tmp = search_result.group()
                param_value = gt_tmp.replace("(", "").replace(")", "").strip()
                # 删除(), 获取参数名
                param_name = re.sub(r"\(.*\)", "", param_text).strip()
                dict_tmp[CCppHeadFileParse.INIT_PARAM_NAME] = param_name
                dict_tmp[CCppHeadFileParse.INIT_PARAM_VALUE] = param_value
                param_list.append(dict_tmp)
            info_dict[CCppHeadFileParse.INIT_PARAM_LIST] = param_list
        else:
            info_dict[CCppHeadFileParse.INIT_PARAM_LIST] = None
        # 删除初始化列表
        method_text = re.sub(r":.*", "", content)
        info_dict = self.__get_method_info(method_text, info_dict)
        return info_dict

    def __get_method_info(self, content, info_dict):
        # 先找括号中的
        search_result = re.search(r"\(.*\)", content)
        if search_result is None:
            # 这里是过滤掉成员变量
            # print(content)
            return info_dict
        gt_tmp = search_result.group()
        param_text = gt_tmp.replace("(", "").replace(")", "")
        param_text_list = param_text.split(",")
        # 判断是否存在参数
        if len(param_text_list) == 1 and param_text_list[0] == "":
            info_dict[CCppHeadFileParse.METHOD_PARAM_LIST] = None
        else:
            param_list = []
            for param_str in param_text_list:
                param_dict = {}
                # 解析出参数
                param_type, param_name = self.__get_param_type_name(param_str)
                param_dict[CCppHeadFileParse.METHOD_PARAM_TYPE] = param_type
                param_dict[CCppHeadFileParse.METHOD_PARAM_NAME] = param_name
                param_list.append(param_dict)
            info_dict[CCppHeadFileParse.METHOD_PARAM_LIST] = param_list
        # 将中间的括号替换为特殊字符(%)号
        after_mid_str = re.sub(r"\(.*\)", "%", content)
        left_right_list = after_mid_str.split("%")
        left_text = left_right_list[0]
        right_text = left_right_list[1]
        # 判断是否是虚函数
        if self.__del_blank_char_and_space(right_text) == "=0":
            info_dict[CCppHeadFileParse.IS_VIRTUAL_METHOD] = True
        else:
            info_dict[CCppHeadFileParse.IS_VIRTUAL_METHOD] = False
        return_type, method_name = self.__get_param_type_name(left_text)
        if return_type == "":
            info_dict[CCppHeadFileParse.METHOD_RETURN_TYPE] = None
        else:
            info_dict[CCppHeadFileParse.METHOD_RETURN_TYPE] = return_type
        info_dict[CCppHeadFileParse.METHOD_NAME] = method_name
        return info_dict

    def __get_param_type_name(self, content):
        split_tmp = self.__space_split(content)
        param_type = ""
        for i in range(len(split_tmp) - 1):
            param_type += split_tmp[i]
            if i != len(split_tmp) - 2:
                param_type += " "
        # 将 * 或者 & 转移位置
        symbol_list = re.findall(r"(\*|&)", split_tmp[-1])
        for symbol in symbol_list:
            param_type += symbol
        param_name = split_tmp[-1].strip()
        # 去除 &或者*
        param_name = re.sub(r"(\*|&)", "", param_name)
        type_name = (param_type, param_name)
        return type_name

    def __space_split(self, content):
        content = content.strip()
        # 如果直接使用 split ，将出现多个错误的空格分割
        str_tmp = re.sub(r"[ ]+", " ", content)
        return str_tmp.split(" ")

    def __del_annotate(self, content):
        content = re.sub(r"//.*", "", content)
        content = re.sub(r"/\*(\s|.)*?\*/", "", content)
        return content


if __name__ == "__main__":
    parse = CCppHeadFileParse()
    parse.parse("../hfiles/sub1/CElement.h")

