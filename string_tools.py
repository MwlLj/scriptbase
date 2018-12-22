# encoding=utf8
import re
import inspect


class CStringTools(object):
	__MODE_SMALL = 1
	__MODE_LARGER = 2
	__MODE_NORMAL = 3
	@classmethod
	def get_current_function_name(cls):
		return inspect.stack()[1][3]

	@classmethod
	def underling2HumpLarger(cls, varName):
		# 将下划线命名转换为驼峰式命名
		if len(varName) == 0 or varName == "":
			return varName
		# 转换为小写
		varName = varName.lower()
		words = varName.split("_")
		length = len(words)
		retStr = ""
		for strTmp in words:
			wordLen = len(strTmp)
			if strTmp == "" or wordLen < 1:
				continue
			firstChar = strTmp[0]
			afterStr = ""
			if wordLen == 1:
				afterStr = firstChar.upper()
			else:
				afterStr = firstChar.upper() + strTmp[1:]
			retStr += afterStr
		return retStr

	@classmethod
	def humpLarger2Underling(cls, varName):
		# 将驼峰式命名转换为下划线命名
		queue = []
		tmp = []
		for ch in varName:
			if ch == ch.upper():
				ch = ch.lower()
				queue.append(1)
			if len(queue) == 2:
				queue = cls._general_version_list_clear(queue)
				queue.append(1)
				tmp.append("_")
			tmp.append(ch)
		return "".join(tmp)

	@classmethod
	def hump2list(cls, varName):
		# 将驼峰式命名分解为数组
		queue = []
		result = []
		tmp = []
		for ch in varName:
			if ch == ch.upper():
				queue.append(1)
			if len(queue) == 2:
				result.append("".join(tmp))
				queue = cls._general_version_list_clear(queue)
				tmp = cls._general_version_list_clear(tmp)
				queue.append(1)
			tmp.append(ch)
		result.append("".join(tmp))
		return result

	@classmethod
	def hump2listSmall(cls, varName):
		# 将驼峰式命名分解为数组
		return cls.__hump2list(varName, CStringTools.__MODE_SMALL)

	@classmethod
	def hump2listNormal(cls, varName):
		return cls.__hump2list(varName, CStringTools.__MODE_NORMAL)

	@classmethod
	def hump2listLarger(cls, varName):
		return cls.__hump2list(varName, CStringTools.__MODE_LARGER)

	@classmethod
	def _general_version_list_clear(cls, li):
		try:
			li.clear()
		except Exception as e:
			li[:] = []
		else:
			pass
		finally:
			pass
		return li

	@classmethod
	def general_version_list_clear(cls, li):
		return cls._general_version_list_clear(li)

	@classmethod
	def __hump2list(cls, varName, mode):
		# 将驼峰式命名分解为数组
		queue = []
		result = []
		tmp = []
		for ch in varName:
			if ch == ch.upper():
				queue.append(1)
			if len(queue) == 2:
				result.append("".join(tmp))
				queue = cls._general_version_list_clear(queue)
				tmp = cls._general_version_list_clear(tmp)
				queue.append(1)
			c = ch
			if mode == CStringTools.__MODE_LARGER:
				c = ch.upper()
			elif mode == CStringTools.__MODE_NORMAL:
				c = ch
			elif mode == CStringTools.__MODE_SMALL:
				c = ch.lower()
			tmp.append(c)
		result.append("".join(tmp))
		return result

	@classmethod
	def serialUpper2SingleUpper(cls, word):
		# 将连续大写的部分转换只有最前面的大写
		result = []
		upper_buf = []
		lower_buf = []
		for char in word:
			if char.upper() == char:
				upper_buf.append(char)
				result.append("".join(lower_buf))
				lower_buf = cls._general_version_list_clear(lower_buf)
			else:
				lower_buf.append(char)
				result.append(cls.upperFirstByte("".join(upper_buf).lower()))
				upper_buf = cls._general_version_list_clear(upper_buf)
		if len(upper_buf) > 0:
			result.append(cls.upperFirstByte("".join(upper_buf).lower()))
		if len(lower_buf) > 0:
			result.append("".join(lower_buf))
		return "".join(result)

	@classmethod
	def list2humpSmall(cls, string_list):
		# 将字符串列表转换为小写开头的驼峰式
		length = len(string_list)
		if length < 2:
			return "".join(string_list)
		i = 0
		tmp = []
		for string in string_list:
			i += 1
			string = string.lower()
			if i > 1:
				string = cls.upperFirstByte(string)
			tmp.append(string)
		return "".join(tmp)

	@classmethod
	def __mode_changed(cls, mode, string):
		c = string
		if mode == CStringTools.__MODE_LARGER:
			c = string.upper()
		elif mode == CStringTools.__MODE_NORMAL:
			c = string
		elif mode == CStringTools.__MODE_SMALL:
			c = string.lower()
		return c

	@classmethod
	def __list2specificSplitChar(cls, string_list, ch, mode):
		tmp = []
		length = len(string_list)
		i = 0
		for string in string_list:
			i += 1
			tmp.append(cls.__mode_changed(mode, string))
			if i < length:
				tmp.append(ch)
		return "".join(tmp)

	@classmethod
	def list2underlingSmall(cls, string_list):
		return cls.__list2specificSplitChar(string_list, "_", CStringTools.__MODE_SMALL)

	@classmethod
	def list2urlSmall(cls, string_list):
		return cls.__list2specificSplitChar(string_list, "/", CStringTools.__MODE_SMALL)

	@classmethod
	def underling2HumpSmall(cls, varName):
		# 将下划线命名转换为驼峰式命名
		if len(varName) == 0 or varName == "":
			return varName
		# 转换为小写
		varName = varName.lower()
		words = varName.split("_")
		length = len(words)
		if length == 1:
			return words[0]
		retStr = words[0]
		for i in range(1, length):
			strTmp = words[i]
			wordLen = len(strTmp)
			if strTmp == "" or wordLen < 1:
				continue
			firstChar = strTmp[0]
			afterStr = ""
			if wordLen == 1:
				afterStr = firstChar.upper()
			else:
				afterStr = firstChar.upper() + strTmp[1:]
			retStr += afterStr
		return retStr

	@classmethod
	def upperFirstByte(cls, word):
		length = len(word)
		if length == 0:
			return word
		after = word[0].upper() + word[1:]
		return after

	@classmethod
	def lowerFirstByte(cls, word):
		length = len(word)
		if length == 0:
			return word
		after = word[0].lower() + word[1:]
		return after

	@classmethod
	def filter_reg_keyword(cls, reg_str):
		reg_str = re.sub(r"\(", "\\(", reg_str)
		reg_str = re.sub(r"\)", "\\)", reg_str)
		reg_str = re.sub(r"\+", "\\+", reg_str)
		reg_str = re.sub(r'\*', '\\*', reg_str)
		return reg_str

	@classmethod
	def is_exist(cls, reg, content):
		search = re.search(reg, content, re.S)
		if search is not None:
			return True
		return False

	@classmethod
	def append_keyword_line_tail(cls, content, keyword, tail_content):
		is_find = False
		buf = ""
		lines = content.splitlines()
		for line in lines:
			buf += line
			search = re.search(r"{0}".format(cls.filter_reg_keyword(keyword)), line)
			if search is not None:
				is_find = True
				buf += tail_content
			buf += "\n"
		return is_find, buf

	@classmethod
	def append_keyword_line_l_t_r_d(cls, content, keyword, left_content="", top_content="", right_content="", down_content=""):
		# 在找到的关键字所在的行的 左 上 右 下 添加指定的文本
		is_find = False
		buf = ""
		lines = content.splitlines()
		for line in lines:
			search = re.search(r"{0}".format(cls.filter_reg_keyword(keyword)), line)
			if search is not None:
				is_find = True
				if top_content != "":
					buf += top_content + "\n"
				if left_content != "":
					buf += left_content
				buf += line
				if right_content != "":
					buf += right_content
					buf += "\n"
				if down_content != "":
					buf += down_content + "\n"
			else:
				buf += line
				buf += "\n"
		return is_find, buf

	@classmethod
	def brace_format(cls, content, replaces):
		content = re.sub(r"{", r"\{", content)
		content = re.sub(r"}", r"\}", content)
		searchs = re.findall(r"(\{(.*?)\})", content)
		fulls = []
		numbers = []
		for search in searchs:
			length = len(search)
			if length != 2:
				raise SystemExit("[Brace Error] {} not match")
			full, number = search
			full = re.sub(r"{", r"\{", full)
			# full = re.sub(r"\\", "", full)
			number = re.sub(r"\\", "", number)
			fulls.append((number, full))
			numbers.append(number)
		number_set = set(numbers)
		if len(number_set) != len(replaces):
			raise SystemExit("CStringTools: [Index Error] {} length != [] length")
		content = re.sub(r"\\", "", content)
		fulls_set = set(fulls)
		fulls_list = list(fulls_set)
		for number, full in fulls_list:
			content = re.sub(full, replaces[int(number)], content)
		return content

	@classmethod
	def get_brace_format_list(cls, content):
		content = re.sub(r"{", r"\{", content)
		content = re.sub(r"}", r"\}", content)
		searchs = re.findall(r"(\{(.*?)\})", content)
		num_max = 0
		fulls = []
		for search in searchs:
			length = len(search)
			if length != 2:
				raise SystemExit("[Brace Error] {} not match")
			full, number = search
			full = re.sub(r"{", r"\{", full)
			# full = re.sub(r"\\", "", full)
			number = re.sub(r"\\", "", number)
			if num_max < int(number):
				num_max = int(number)
			fulls.append((int(number), full))
		return fulls, num_max

	@classmethod
	def get_brace_format_list2(cls, content):
		num_max = 0
		fulls = []
		number_tmp = []
		full_tmp = ""
		is_in_symbol = False
		last_is_other = False
		next_is_other = False
		for item in content:
			if item == "{":
				full_tmp = '\\{'
				is_in_symbol = True
				last_is_other = True
			elif item == "}":
				next_is_other = True
				full_tmp += "\\}"
				number = int("".join(number_tmp))
				if num_max < number:
					num_max = number
				fulls.append((number, full_tmp, last_is_other, next_is_other))
				full_tmp = ""
				is_in_symbol = False
				number_tmp.clear()
			else:
				full_tmp += item
				if last_is_other is True and is_in_symbol is False:
					last_is_other = False
				if next_is_other is True and is_in_symbol is False:
					next_is_other = False
				if is_in_symbol is True:
					number_tmp.append(item)
		return fulls, num_max

	@classmethod
	def num2binstring(cls, value):
		return bin(value).replace("0b", "")

	@classmethod
	def binary_bit_combination(cls, count):
		"""
		if count = 2
		return:
			[[0, 0], [0, 1], [1, 0], [1, 1]]
		"""
		ret = []
		max_value = 2 ** count
		for i in range(max_value):
			r = cls.num2binstring(i)
			if len(r) < count:
				r = r.rjust(count, "0")
			length = len(r)
			li = [int(item) for item in r]
			ret.append(li)
		return ret


if __name__ == "__main__":
	CStringTools.underling2HumpLarger("T_AASP_LOGIN_AUTH_RSP")
	ret = CStringTools.underling2HumpSmall("T_AASP_LOGIN_AUTH_RSP")
	ret = CStringTools.upperFirstByte("helloWorld")
	ret = CStringTools.humpLarger2Underling("CTTwspLoginAuthReq")
	ret = CStringTools.hump2list("CPostRecognitionRequest")
	ret = CStringTools.list2humpSmall(['c', 'post', 'network', 'param', 'request'])
	is_find, ret = CStringTools.append_keyword_line_l_t_r_d(
		"""
class CGetNetworkStatusRequest;
class CGetNetworkStatusReply;
const static std::string networkStatus("/1.0/testjson/networkStatus"); // get
		"""
		, "std::string networkStatus", right_content=" updated", top_content="class CUpdatedNetworkStatusRequest;")
	ret = CStringTools.list2underlingSmall(['C', 'Post', 'Network', 'Param', 'Request'])
	ret = CStringTools.serialUpper2SingleUpper("CUpdatedIDCardDiscoveryRequestQQQ")
	ret = CStringTools.brace_format("xxx{0}yyy{1}zzz{0}", ["123", "789"])
	ret = CStringTools.get_brace_format_list("xxx{0}yyy{1}zzz{0}")
	ret = CStringTools.binary_bit_combination(2)
	print(ret)
