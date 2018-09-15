# encoding=utf8
import os
import sqlite3
import shutil


class ISqliteOperate(object):
	def get_tables(self):
		return []


class CSqliteOperate(ISqliteOperate):
	def __init__(self, db_path):
		self.m_connect = None
		self.m_cursor = None
		user_dir = os.path.dirname(db_path)
		if os.path.exists(user_dir) is False:
			os.makedirs(user_dir)
		if os.path.exists(db_path) is False:
			# 创建db文件
			fp = None
			try:
				fp = open(db_path, "w+", encoding="utf8")
			except Exception as e:
				raise RuntimeError("open db file error")
			else:
				pass
			finally:
				if fp is not None:
					fp.close()
		# 连接
		self.m_connect = sqlite3.connect(db_path)
		self.m_cursor = self.m_connect.cursor()
		self.__create_table()

	def __create_table(self):
		try:
			for table in self.get_tables():
				self.m_cursor.execute(table)
		except Exception as e:
			raise RuntimeError("create table error")
		else:
			pass
		finally:
			pass

	def insert(self, sql):
		try:
			self.m_cursor.execute(sql)
			self.m_connect.commit()
		except Exception as e:
			raise RuntimeError("insert error")
		else:
			pass
		finally:
			pass

	def update(self, sql):
		self.insert(sql)

	def query(self, sql):
		res = None
		try:
			self.m_cursor.execute(sql)
			res = self.m_cursor.fetchall()
		except Exception as e:
			raise
		else:
			pass
		finally:
			pass
		return res

	def close(self):
		if self.m_connect is not None:
			self.m_connect.close()


if __name__ == "__main__":
	operate = CSqliteOperate("../createsvr/user/sqlite/server_create.db")
	operate.close()
