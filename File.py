import os
import chardet


# 其实相当于FCB，记录文件信息，具体文件数据储存在模拟磁盘
class File:
    def __init__(self, path, name):
        self.fileName = name
        self.filePath = path

        # 簇号记录文件磁盘位置
        self.start_cluster = None
        self.end_cluster = None

        # 检查文件夹是否存在，不存在则创建文件夹
        if not os.path.exists(self.filePath):
            print("文件夹不存在！无法创建文件")
        else:
            open(self.filePath + self.fileName, "w")
            if os.path.exists(self.filePath + self.fileName):
                print("文件已创建")
            else:
                print("文件创建失败")
            self.space = os.path.getsize(self.filePath + self.fileName)

    def get_name(self):
        return self.fileName

    def get_path(self):
        return os.path.abspath(self.filePath) + "\\"

    def get_filepath(self):
        return os.path.abspath(self.filePath) + "\\" + self.fileName  # 给出绝对路径

    def get_space(self):
        return os.path.getsize(self.filePath + self.fileName)

    def open_file(self):
        # print(os.path.abspath(self.filePath)) 测试路径
        # print(self.filePath + self.fileName)
        os.startfile(os.path.abspath(self.filePath) + "\\" + self.fileName)

    def get_data(self):
        # 探测文件编码
        with open(self.filePath + self.fileName, 'rb') as f1:
            file_content = f1.read()
        result = chardet.detect(file_content)
        encoding = result['encoding']

        # 使用探测到的编码打开文件
        with open(self.filePath + self.fileName, 'r', encoding=encoding) as f2:
            data = f2.read()
        print(data)
        return data

    def write_data(self, data):
        with open(self.filePath + self.fileName, 'w') as f:
            f.write(data)
