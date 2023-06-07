import os
from File import *
from PyQt5 import Qt, QtGui, QtWidgets
from Main import Type

import shutil
import psutil

class Folder:
    def __init__(self, path, name):
        try:
            os.mkdir(path + name + '/')
        except:
            print("文件夹创建失败")
        self.folderPath = path
        self.folderName = name
        self.fileList = []  # 文件夹中包含的文件
        self.folderList = []  # 文件夹中包含的文件夹

        # 簇号记录文件磁盘位置
        self.start_cluster = None
        self.end_cluster = None

    def get_name(self):
        return self.folderName

    def get_path(self):
        return os.path.abspath(self.folderPath) + "\\"

    def get_filenum(self):
        return len(self.fileList) + len(self.folderList)

    def get_space(self):
        return os.path.getsize(self.folderPath + self.folderName)

    def get_folderpath(self):
        return os.path.abspath(self.folderPath) + "\\" + self.folderName  # 给出绝对路径

    def search_file(self, filename, list, type):
        if type == Type.File:
            for i in list:
                if i.fileName == filename:
                    return True
            else:
                return False
        else:
            for i in list:
                if i.folderName == filename:
                    return True
            else:
                return False

    def create_file(self, newfile, disk):
        # 计算空间，只要还有空闲簇都能创建，空文件占用一个簇，当该文件文件输入内容超过该簇后，申请新簇，直到没有空闲簇
        cluster_id = None
        for i in disk:
            if i["status"] == "free":
                cluster_id = i["cluster_id"]
                break
        if cluster_id is not None:
            if self.search_file(newfile, self.fileList, Type.File):
                QtWidgets.QMessageBox.warning(None, '创建文件', f'该文件夹存在同名文件！创建失败')
            else:
                file = File(self.folderPath + self.folderName + '/', newfile)
                file.start_cluster = file.end_cluster = cluster_id  # 相当于FCB/目录表记录起始和终止簇
                if self.start_cluster is None and self.end_cluster is None:
                    self.start_cluster = self.end_cluster = cluster_id
                else:
                    disk[self.end_cluster]["next"] = cluster_id  # 更新该文件夹所占用的簇
                    self.end_cluster = cluster_id
                disk[cluster_id]["status"] = "busy"
                self.fileList.append(file)  # 创建好一个空文件
        else:
            QtWidgets.QMessageBox.warning(None, '创建文件', f'创建文件失败!空间不足')

    def delete_file(self, filename, disk):
        for i in self.fileList:
            if i.fileName == filename:
                self.fileList.remove(i)  # 移除后就不用管了，此时目录表中不存在该文件
                os.remove(i.filePath + i.fileName)  # 删除本地的文件
                # 处理模拟磁盘的变动,从该目录占有的簇中查找到该文件位置
                cluster = disk[self.start_cluster]
                while cluster["next"] is not None:
                    if cluster["next"] == i.start_cluster:
                        cluster["next"] = disk[i.end_cluster]["next"]  # 剔除链,重连整个链
                        break
                    cluster = disk[cluster["next"]]
                # 将原来使用的簇清空内容释放
                cluster = disk[i.start_cluster]
                while True:
                    cluster["data"] = None
                    cluster["status"] = "free"
                    cluster["size"] = 1024
                    mid_id = cluster["next"]
                    cluster["next"] = None
                    if mid_id is not None and cluster != disk[i.end_cluster]:
                        cluster = disk[mid_id]
                    else:
                        break
                break
        else:
            QtWidgets.QMessageBox.warning(None, '删除文件', f'删除文件失败!文件不存在')

    # 更新该文件夹下所有文件的路径
    def reset_path(self):
        for i in self.folderList:
            i.folderPath = self.folderPath + self.folderName + '/'
            i.reset_path()
        for j in self.fileList:
            j.filePath = self.folderPath + self.folderName + '/'

    def rename_file(self, old_name, new_name):
        _, old_ext = os.path.splitext(old_name)
        _, new_ext = os.path.splitext(new_name)
        if old_ext != new_ext:
            QtWidgets.QMessageBox.warning(None, '重命名', f'重命名失败！\n不支持格式更改：' + old_ext + '->' + new_ext)
            return
        for i in self.fileList:
            if i.fileName == old_name:
                # 检查文件是否被使用
                file_path = i.get_filepath()
                for process in psutil.process_iter():
                    try:
                        process_files = process.open_files()
                        for process_file in process_files:
                            if process_file.path == file_path:
                                print(f'文件"{file_path}"正在被"{process.name()}"进程使用')
                                break
                        else:
                            i.fileName = new_name
                            os.rename(i.filePath + old_name, i.filePath + new_name)
                            break
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                break
        else:
            QtWidgets.QMessageBox.warning(None, '重命名', f'重命名失败！文件不存在')

    def create_folder(self, newfolder, disk):
        # 文件夹也属于一种特殊的文件，空文件夹也要占用一个簇
        cluster_id = None
        for i in disk:
            if i["status"] == "free":
                cluster_id = i["cluster_id"]
                break
        if cluster_id is not None:
            if self.search_file(newfolder, self.folderList, Type.Folder):
                QtWidgets.QMessageBox.warning(None, '创建文件夹', f'该文件夹存在同名文件夹！创建失败')
            else:
                folder = Folder(self.folderPath + self.folderName + "/", newfolder)
                folder.start_cluster = folder.end_cluster = cluster_id
                if self.start_cluster is None and self.end_cluster is None:
                    self.start_cluster = self.end_cluster = cluster_id
                else:
                    disk[self.end_cluster]["next"] = cluster_id  # 更新该文件夹所占用的簇
                    self.end_cluster = cluster_id
                disk[cluster_id]["status"] = "busy"
                self.folderList.append(folder)
        else:
            QtWidgets.QMessageBox.warning(None, '创建文件夹', f'创建文件夹失败!空间不足')

    def delete_folder(self, foldername, disk):
        for i in self.folderList:
            if i.folderName == foldername:
                self.folderList.remove(i)  # 移除后就不用管了，此时目录表中不存在该文件夹及其下的所有内容
                shutil.rmtree(i.folderPath + i.folderName + '/')  # 删除本地的内容
                # 处理模拟磁盘的变动,从该目录占有的簇中查找到该文件位置
                cluster = disk[self.start_cluster]
                while cluster["next"] is not None:
                    if cluster["next"] == i.start_cluster:
                        cluster["next"] = disk[i.end_cluster]["next"]  # 剔除链,重连整个链
                        break
                    cluster = disk[cluster["next"]]
                # 将原来使用的簇清空内容释放
                cluster = disk[i.start_cluster]
                while True:
                    cluster["data"] = None
                    cluster["status"] = "free"
                    cluster["size"] = 1024
                    mid_id = cluster["next"]
                    cluster["next"] = None
                    if mid_id is not None and cluster != disk[i.end_cluster]:
                        cluster = disk[mid_id]
                    else:
                        break
                break
        else:
            # 如果进入该删除文件夹函数，但是没有删除成功，有可能是无后缀名空文件
            self.delete_file(foldername, disk)

    def rename_folder(self, old_name, new_name):
        for i in self.folderList:
            if i.folderName == old_name:
                # 检查文件夹是否被使用
                folder_path = i.get_folderpath()
                for process in psutil.process_iter():
                    try:
                        process_files = process.open_files()
                        for process_file in process_files:
                            if process_file.path.startswith(folder_path):
                                print(f'文件夹"{folder_path}"正在被"{process.name()}"进程使用')
                                break
                        else:
                            # 如果没有找到正在使用文件夹的进程，则进行文件夹重命名操作
                            i.folderName = new_name
                            os.rename(i.folderPath + old_name + '/', i.folderPath + new_name + '/')
                            # 目录路径下得所有文件的路径全部更新
                            i.reset_path()
                            break
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                break
        else:
            QtWidgets.QMessageBox.warning(None, '重命名', f'重命名失败！文件夹不存在')
