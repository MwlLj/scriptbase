# encoding=utf8
import sys


class ICmdlineHandle(object):
    def get_register_dict(self):
        """{"-l", 所需的参数个数}, 如果个数是 -1 表示不限制"""
        return {}

    def single_option(self, option, param_list):
        pass

    def param_error(self, option):
        pass

    def parse_end(self):
        pass


class CCmdlineHandle(ICmdlineHandle):
    def __init__(self):
        pass

    def parse(self):
        args = sys.argv
        option_dict = self.get_register_dict()
        if len(option_dict) == 0 or len(args) == 1:
            self.single_option("", [])
            self.parse_end()
            return
        for option in option_dict.keys():
            # 判断有效性
            if option in args:
                index = args.index(option)
                param_len = option_dict[option]
                if param_len == -1:
                    self.__handle_change_length_param(args, index, option)
                else:
                    self.__handle_fix_length_param(args, index, param_len, option)
        self.parse_end()

    def __handle_change_length_param(self, args, index, option):
        option_dict = self.get_register_dict()
        option_list = option_dict.keys()
        # 查找下一个关键字
        params = []
        for i in range(index + 1, len(args)):
            try:
                # 判断是否越界
                args[i]
            except Exception as e:
                self.param_error(option)
                break
            # 无越界
            param = args[i]
            if param in option_list:
                break
            # 无越界，并且不是下一个操作符
            params.append(param)
        self.single_option(option, params)

    def __handle_fix_length_param(self, args, index, param_len, option):
        if len(args) < index + 1 + param_len:
            self.param_error(option)
        else:
            params = []
            for i in range(param_len):
                params.append(args[index + 1 + i])
            self.single_option(option, params)

