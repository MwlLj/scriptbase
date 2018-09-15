#encoding=utf8
import xlrd


class CParseExcel(object):
	SHEET_INFOS = "sheet_infos"
	SHEET_INFO = "sheet_info"
	SHEET_NAME = "sheet_name"
	SHEET_INDEX = "sheet_index"
	ROW_VALUES = "row_values"
	ROW_VALUE = "row_value"
	COL_VALUES = "col_values"
	COL_VALUE = "col_value"
	VALUE_INFOS = "value_infos"
	VALUE = "value"
	ROW_INDEX = "row_index"
	COL_INDEX = "col_index"
	def __init__(self, file_path):
		self.m_file_path = file_path
		self.m_info_dict = {}

	def parse(self):
		excel_data = xlrd.open_workbook(self.m_file_path)
		sheets = excel_data.sheets()
		sheet_len = len(sheets)
		sheet_names = excel_data.sheet_names()
		sheet_infos = []
		for i in range(sheet_len):
			sheet_info = {}
			sheet = excel_data.sheet_by_index(i)
			sheet_name = sheet_names[i]
			row_len = sheet.nrows
			col_len = sheet.ncols
			row_values = []
			for row in range(1, row_len):
				row_value = {}
				col_values = []
				for col in range(col_len):
					col_value = {}
					value = sheet.cell(row, col).value
					col_value[CParseExcel.COL_INDEX] = col
					col_value[CParseExcel.VALUE] = value
					col_values.append(col_value)
				row_value[CParseExcel.ROW_INDEX] = row
				row_value[CParseExcel.COL_VALUES] = col_values
				row_values.append(row_value)
			sheet_info[CParseExcel.ROW_VALUES] = row_values
			sheet_info[CParseExcel.SHEET_NAME] = sheet_name
			sheet_info[CParseExcel.SHEET_INDEX] = i
			sheet_infos.append(sheet_info)
		self.m_info_dict[CParseExcel.SHEET_INFOS] = sheet_infos

	def get_info_dict(self):
		return self.m_info_dict


if __name__ == "__main__":
	parser = CParseExcel(r"../gen_person_info/file/test.xls")
	parser.parse()
	print(parser.get_info_dict())
