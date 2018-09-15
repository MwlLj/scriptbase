# encoding=utf8
import hashlib
import file_encoding


class CGetMd5(object):
    def __init__(self):
        self.m_md5 = None

    def calc_md5(self, src):
        self.m_md5 = hashlib.md5()
        if type(src) == type(""):
            self.m_md5.update(src.encode("utf8"))
        else:
            self.m_md5.update(src)
        return self.m_md5.hexdigest()


if __name__ == "__main__":
    obj = CGetMd5()
    result = obj.calc_md5("123456")
    print(result)
    result = obj.calc_md5("123456")
    print(result)

