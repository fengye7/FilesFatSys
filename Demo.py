import os
import pickle
from PyQt5 import QtWidgets, QtCore

class FileSystem:
    def __init__(self):
        self.files = []     # 存储文件系统中的文件和目录
        self.fat = []       # 文件分配表，用于管理文件的物理地址
        self.root_dir = {"name": "/", "type": "directory", "subitems": []}   # 根目录
        self.current_dir = self.root_dir   # 当前目录

    def format(self):
        # 格式化文件系统
        self.files = []
        self.fat = []
        self.root_dir = {"name": "/", "type": "directory", "subitems": []}
        self.current_dir = self.root_dir

    def create_dir(self, dirname):
        # 创建新目录
        dir = {"name": dirname, "type": "directory", "subitems": []}
        self.current_dir["subitems"].append(dir)

    def delete_dir(self, dirname):
        # 查找目录
        for i, item in enumerate(self.current_dir["subitems"]):
            if item["name"] == dirname and item["type"] == "directory":
                # 删除目录
                del self.current_dir["subitems"][i]
                return

        raise FileNotFoundError("目录不存在！")

    def display_dir(self):
        # 显示当前目录
        print("当前目录：", self.current_dir["name"])
        print("文件列表：")
        for item in self.current_dir["subitems"]:
            print(item["name"], item["type"])

    def change_dir(self, dirname):
        # 切换目录
        for item in self.current_dir["subitems"]:
            if item["name"] == dirname and item["type"] == "directory":
                self.current_dir = item
                return

        raise FileNotFoundError("目录不存在！")

    def create_file(self, filename):
        # 检查文件是否已经存在
        for item in self.current_dir["subitems"]:
            if item["name"] == filename and item["type"] == "file":
                raise FileExistsError("文件已经存在！")

        # 分配新的物理地址
        if len(self.fat) == 0:
            address = 0
        else:
            address = self.fat[-1]["end"] + 1

        # 创建新文件
        file = {"name": filename, "type": "file", "address": address, "length": 0}
        self.current_dir["subitems"].append(file)
        self.fat.append({"start": address, "end": address, "next": None})

    def open_file(self, filename):
        # 查找文件
        for item in self.current_dir["subitems"]:
            if item["name"] == filename and item["type"] == "file":
                return item

        raise FileNotFoundError("文件不存在！")

    def write_file(self, file, data):
        # 写文件
        start = file["address"]
        end = start + len(data) - 1

        # 更新 FAT 表
        current = self.fat[start]
        while current is not None:
            current["end"] = end
            current = self.fat[current["next"]]

        # 更新文件长度
        file["length"] = len(data)

        # 更新文件内容
        with open("filesystem.dat", "r+b") as f:
            f.seek(start)
            f.write(data)

    def read_file(self, file):
        # 读文件
        start = file["address"]
        end = file["address"] + file["length"] - 1

        # 读取文件内容
        with open("filesystem.dat", "rb") as f:
            f.seek(start)
            data = f.read()

        return data

    def delete_file(self, filename):
        # 查找文件
        for i, item in enumerate(self.current_dir["subitems"]):
            if item["name"] == filename and item["type"] == "file":
                # 删除文件
                self.current_dir["subitems"].pop(i)

                # 更新 FAT 表
                start = item["address"]
                current = self.fat[start]
                while current is not None:
                    for i in range(current["start"], current["end"]+1):
                        self.fat[i] = None
                    current = self.fat[current["next"]]

                return

        raise FileNotFoundError("文件不存在！")

    def save_to_file(self):
        # 将文件系统保存到文件中
        with open("filesystem.dat", "wb") as f:
            pickle.dump((self.files, self.fat, self.root_dir, self.current_dir), f)

    def load_from_file(self):
        # 从文件中加载文件系统
        if os.path.exists("filesystem.dat"):
            with open("filesystem.dat", "rb") as f:
                self.files, self.fat, self.root_dir, self.current_dir = pickle.load(f)

class FileSystemUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建文件系统
        self.fs = FileSystem()

        # 创建界面
        self.setWindowTitle("文件管理系统")
        self.setGeometry(100, 100, 600, 400)

        # 创建控件
        self.dir_list = QtWidgets.QListWidget()
        self.file_list = QtWidgets.QListWidget()
        self.dir_label = QtWidgets.QLabel("目录名：")
        self.dir_edit = QtWidgets.QLineEdit()
        self.create_dir_button = QtWidgets.QPushButton("创建目录")
        self.delete_dir_button = QtWidgets.QPushButton("删除目录")
        self.file_label = QtWidgets.QLabel("文件名：")
        self.file_edit = QtWidgets.QLineEdit()
        self.create_file_button = QtWidgets.QPushButton("创建文件")
        self.open_file_button = QtWidgets.QPushButton("打开文件")
        self.close_file_button = QtWidgets.QPushButton("关闭文件")
        self.write_file_button = QtWidgets.QPushButton("写文件")
        self.read_file_button = QtWidgets.QPushButton("读文件")
        self.delete_file_button = QtWidgets.QPushButton("删除文件")

        # 布局控件
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QGridLayout()
        central_widget.setLayout(layout)
        layout.addWidget(self.dir_list, 0, 0, 1, 2)
        layout.addWidget(self.file_list, 0, 2, 1, 2)
        layout.addWidget(self.dir_label, 1, 0)
        layout.addWidget(self.dir_edit, 1, 1)
        layout.addWidget(self.create_dir_button, 1, 2)
        layout.addWidget(self.delete_dir_button, 1, 3)
        layout.addWidget(self.file_label, 2, 0)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(self.create_file_button, 2, 2)
        layout.addWidget(self.open_file_button, 2, 3)
        layout.addWidget(self.close_file_button, 3, 2)
        layout.addWidget(self.write_file_button, 3, 3)
        layout.addWidget(self.read_file_button, 4, 2)
        layout.addWidget(self.delete_file_button, 4, 3)

        # 绑定事件
        self.create_dir_button.clicked.connect(self.create_dir)
        self.delete_dir_button.clicked.connect(self.delete_dir)
        self.create_file_button.clicked.connect(self.create_file)
        self.open_file_button.clicked.connect(self.open_file)
        self.close_file_button.clicked.connect(self.close_file)
        self.write_file_button.clicked.connect(self.write_file)
        self.read_file_button.clicked.connect(self.read_file)
        self.delete_file_button.clicked.connect(self.delete_file)

        # 初始化界面
        self.update_file_list()
        self.update_dir_list()

    def update_file_list(self):
        # 更新文件列表
        self.file_list.clear()
        for item in self.fs.current_dir["subitems"]:
            if item["type"] == "file":
                self.file_list.addItem(item["name"])

    def update_dir_list(self):
        # 更新目录列表
        self.dir_list.clear()
        for item in self.fs.current_dir["subitems"]:
            if item["type"] == "directory":
                self.dir_list.addItem(item["name"])

    def create_dir(self):
        # 创建目录
        dirname = self.dir_edit.text()
        try:
            self.fs.create_dir(dirname)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", str(e))
        else:
            self.update_dir_list()

    def delete_dir(self):
        # 删除目录
        dirname = self.dir_edit.text()
        try:
            self.fs.delete_dir(dirname)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", str(e))
        else:
            self.update_dir_list()

    def create_file(self):
        # 创建文件
        filename = self.file_edit.text()
        try:
            self.fs.create_file(filename)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", str(e))
        else:
            self.update_file_list()

    def open_file(self):
        # 打开文件
        filename = self.file_edit.text()
        try:
            self.current_file = self.fs.open_file(filename)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", str(e))
        else:
            QtWidgets.QMessageBox.information(self, "提示", "文件已打开！")

import sys
if __name__ == '__main__':
   app = QtWidgets.QApplication(sys.argv)
   MainWindow = QtWidgets.QMainWindow() # 创建窗体对象
   ui = FileSystemUI() # 创建PyQt设计的窗体对象
   ui.setupUi(MainWindow) # 调用PyQt窗体的方法对窗体对象进行初始化设置
   MainWindow.show() # 显示窗体
   sys.exit(app.exec_()) # 程序关闭时退出进程