import os.path

from Frame import *
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt
from datetime import datetime
from enum import Enum
import atexit
import pickle  # 处理序列化
import watchdog
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from FileManage import *


# 双击的对象类型
class Type(Enum):
    Folder = 1
    File = 2


class Ui_Fengye7_FileSystem(Ui_FileSysFrame):
    # 构造函数
    def __init__(self, FileSystem):
        self.FileSys = FileManage("./", "Fengye7_FileSystem")
        self.setupUi(FileSystem)  # 使用的.py由.ui文件转化而来，方便实时更改.ui
        self.finishUI()  # 完成界面的初始化

        # 声明在groupBox创建右键菜单
        self.groupBox.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        self.groupBox.customContextMenuRequested.connect(self.create_rightmenu)  # 连接到菜单显示函数

        # 链接写入磁盘和退出
        actionA = QtWidgets.QAction(u'写入磁盘', self.menu_write)
        self.menu_write.addAction(actionA)  # 把动作A选项添加到菜单
        actionA.triggered.connect(self.write_disk)

        actionB = QtWidgets.QAction(u'写入目录', self.menu_write)
        self.menu_write.addAction(actionB)  # 把动作A选项添加到菜单
        actionB.triggered.connect(self.write_directory)

        actionC = QtWidgets.QAction(u'退出程序', self.menu_exit)
        self.menu_exit.addAction(actionC)  # 把动作A选项添加到菜单
        actionC.triggered.connect(self.exit_app)

        actionD = QtWidgets.QAction(u'格式化', self.menu_format)
        self.menu_format.addAction(actionD)  # 把动作A选项添加到菜单
        actionD.triggered.connect(self.format)

        # atexit.register(self.write_disk)  # 程序退出时自动写入，防止忘记___这里和格式化操作冲突，格式化操作后退出又将格式化的磁盘文件给改变了
        # atexit.register(self.write_directory)

        # 链接recover刷新显示文件列表
        self.RecoverButton.clicked.connect(self.recover_table)

        # 地址栏添加跳转操作
        self.AddressBar.setReadOnly(False)  # 设置为可编辑
        self.AddressBar.editingFinished.connect(self.jump_path)  # 连接函数

        # 搜索栏
        self.SearchBar.setReadOnly(False)
        self.SearchBar.returnPressed.connect(self.search_file)

        # 链接上一级按钮
        self.BackUp.clicked.connect(self.back_to_father)

    # 按钮返回上一级目录
    def back_to_father(self):
        mid_folder = self.search_ob(self.FileSys,
                                    self.AddressBar.text())  # 获取文件对象,从系统开始文件夹开始递归搜索
        if mid_folder is not None:
            targetfolder = self.search_ob(self.FileSys,
                                          mid_folder.folderPath)  # 获取文件对象,从系统开始文件夹开始递归搜索
            if targetfolder is not None:
                self.tableWidget.setRowCount(0)  # 清空列表行
                self.tableWidget.clearContents()  # 清空内容
                self.show_table(targetfolder)  # 展示新位置
            else:
                QtWidgets.QMessageBox.warning(None, 'error', f'未知问题返回失败！')
        else:
            QtWidgets.QMessageBox.warning(None, 'error', f'未知问题返回失败！')

    # 搜索栏函数
    def search_file(self):
        target_list = []
        bar_text = self.SearchBar.text()

        def sub_search(sourse):
            for i in sourse.folderList:
                if bar_text in i.folderName:
                    target_list.append(i)
                sub_search(i)
            for j in sourse.fileList:
                if bar_text in j.fileName:
                    target_list.append(j)

        sub_search(self.FileSys)  # 获得目标的list

        new_widget = QtWidgets.QDialog()
        new_widget.setWindowTitle("搜索结果")
        new_widget.move(self.SearchBar.pos().x(), self.SearchBar.pos().y() + 20)
        new_widget.resize(400, 500)

        layout = QtWidgets.QVBoxLayout()
        new_widget.setLayout(layout)

        v_table = QtWidgets.QTableWidget()
        v_table.setColumnCount(1)
        v_table.setColumnWidth(0, 400)
        v_table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        v_table.setHorizontalHeaderLabels(["结果列表"])
        layout.addWidget(v_table)

        def double_click(row, column):
            _, file_ext = os.path.splitext(target_list[row].get_name())
            # 双击文件夹
            if file_ext == "":
                if target_list[row] is not None:
                    self.tableWidget.setRowCount(0)  # 清空列表行
                    self.tableWidget.clearContents()  # 清空内容
                    try:
                        self.show_table(target_list[row])  # 展示新位置
                    except:
                        QtWidgets.QMessageBox.information(None, 'error', '该对象是无后缀名的文件，暂不支持打开！')
                        pass
            # 双击文件
            else:
                if target_list[row] is not None:
                    self.on_modified(target_list[row])

        # 链接函数，这个cell链接自动传入row,column
        v_table.cellDoubleClicked.connect(double_click)

        # 添加选项
        for k in target_list:
            v_table.insertRow(v_table.rowCount())  # 添加行
            newItem = QtWidgets.QTableWidgetItem(QtGui.QIcon("./imags/answer.png"), k.get_name())
            v_table.setItem(v_table.rowCount() - 1, 0, newItem)
        new_widget.exec_()

    # 刷新窗口中的table
    def recover_table(self):
        tagetfolder = self.search_ob(self.FileSys,
                                     self.AddressBar.text())  # 获取文件对象,从系统开始文件夹开始递归搜索
        if tagetfolder is not None:
            self.tableWidget.setRowCount(0)  # 清空列表行
            self.tableWidget.clearContents()  # 清空内容
            self.show_table(tagetfolder)  # 展示新位置
        self.treeWidget.clear()  # 清空
        self.show_list(self.treeWidget, self.FileSys.folderList, Type.Folder)  # 重建

    # 将模拟的磁盘的内容写入本地
    def write_disk(self):
        # 给一个字符串副本
        with open("./Fengye7_FileSystem/disk.txt", 'w') as f:
            for block in self.FileSys.disk:
                f.write(str(block) + '\n')
        # 实际的模拟磁盘
        # 如果您想将一个字典对象写入文件，您需要将其序列化为一个字节串对象。在Python中，可以使用pickle或json模块来序列化和反序列化Python对象。
        with open('./Fengye7_FileSystem/disk.pickle', 'wb') as f:
            pickle.dump(self.FileSys.disk, f)

    # 将文件结构转为目录储存到本地磁盘
    def write_directory(self):
        # Serialize the file structure to a dictionary
        def serialize_file(file):
            file_dict = {
                'path': file.filePath,
                'name': file.fileName,
                'start_cluster': file.start_cluster,
                'end_cluster': file.end_cluster
            }
            return file_dict

        # Serialize the folder structure to a dictionary
        def serialize_folder(folder):
            folder_dict = {
                'path': folder.folderPath,
                'name': folder.folderName,
                'file_list': [serialize_file(f) for f in folder.fileList],
                'folder_list': [serialize_folder(f) for f in folder.folderList],
                'start_cluster': folder.start_cluster,
                'end_cluster': folder.end_cluster
            }
            return folder_dict

        root_folder_dict = serialize_folder(self.FileSys)  # 将整个管理系统文件树转为字典
        # Save the folder structure to a file
        with open('./Fengye7_FileSystem/directory.pickle', 'wb') as f:
            pickle.dump(root_folder_dict, f)
        # 给一个字符串副本
        with open("./Fengye7_FileSystem/directory.txt", 'w') as f:
            f.write(str(root_folder_dict))

    # 退出程序
    def exit_app(self):
        self.write_disk()  # 通过退出程序按钮退出的提供自动保存的功能，防止忘记
        self.write_directory()
        QtCore.QCoreApplication.exit()

    # 完善UI界面
    def finishUI(self):
        # UI界面中添加目录
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.header().setMinimumSectionSize(500)  # 添加水平滚动条，尽量把这一列的尺寸设置大一点
        self.treeWidget.itemClicked.connect(self.enter_list)  # 处理列表上的点击事件
        self.show_list(self.treeWidget, self.FileSys.folderList, Type.Folder)  # 底层文件夹的显示
        # self.show_list(self.treeWidget, self.FileSys.fileList, Type.File)  # 底层文件的显示

        # 初始化展示第一个文件夹的信息,同时处理地址栏
        self.tableWidget.setColumnCount(4)  # 设置表格列数
        self.tableWidget.setColumnWidth(0, 290)  # 设置表格列宽
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 150)
        self.tableWidget.setColumnWidth(3, 150)
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        self.tableWidget.itemDoubleClicked.connect(self.enter_item)  # 链接函数处理点击
        self.tableWidget.itemClicked.connect(self.show_below)  # 处理下框
        self.tableWidget.setHorizontalHeaderLabels(["名称", "修改日期", "类型", "大小"])  # 设置表头
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  # 设置整行同时选中
        self.show_table(self.FileSys)  # 调用函数展示表

        # 设置图标
        self.SearchLabel.setPixmap(QtGui.QPixmap("./imags/search.png"))
        self.SearchLabel.setScaledContents(True)

    # 处理下框显示
    def show_below(self):
        selecteditem = self.search_ob(self.FileSys, self.AddressBar.text() + self.tableWidget.selectedItems()[0].text())
        if selecteditem is not None:
            self.selected_item_num.setText("选中1个项目")
            self.selected_item_size.setText(str(selecteditem.get_space() / 1024) + "KB")

    # 创建右键菜单函数
    def create_rightmenu(self):
        # 菜单对象
        groupBox_menu = QtWidgets.QMenu(self.groupBox)

        actionA = QtWidgets.QAction(u'新建文件', groupBox_menu)
        groupBox_menu.addAction(actionA)  # 把动作A选项添加到菜单

        actionB = QtWidgets.QAction(u'新建文件夹', groupBox_menu)
        groupBox_menu.addAction(actionB)

        actionC = QtWidgets.QAction(u'删除', groupBox_menu)
        groupBox_menu.addAction(actionC)

        actionD = QtWidgets.QAction(u'重命名', groupBox_menu)
        groupBox_menu.addAction(actionD)

        actionE = QtWidgets.QAction(u'属性', groupBox_menu)
        groupBox_menu.addAction(actionE)

        actionA.triggered.connect(self.create_file)
        actionB.triggered.connect(self.create_folder)
        actionC.triggered.connect(self.delete_ob)
        actionD.triggered.connect(self.rename_ob)
        actionE.triggered.connect(self.show_attributes)

        groupBox_menu.popup(QtGui.QCursor.pos())  # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单,exec_,popup两个都可以，

    # 新建文件
    def create_file(self):
        # 弹出一个输入对话框，让用户输入新文件名称
        file_name, ok = QtWidgets.QInputDialog.getText(None, '创建文件', '请输入新文件名称：')
        if ok:
            targetfolder = self.search_ob(self.FileSys, self.AddressBar.text())  # 获取文件对象,从系统开始文件夹开始递归搜索
            if targetfolder is not None:
                targetfolder.create_file(file_name, self.FileSys.disk)
                QtWidgets.QMessageBox.information(None, '创建文件', '文件创建成功！')
                self.recover_table()
            else:
                QtWidgets.QMessageBox.warning(None, '创建文件', f'创建文件失败：找不到父文件夹')

    # 新建文件夹
    def create_folder(self):
        # 弹出一个输入对话框，让用户输入新文件夹名称
        file_name, ok = QtWidgets.QInputDialog.getText(None, '创建文件夹', '请输入新文件夹名称：')
        if ok:
            targetfolder = self.search_ob(self.FileSys, self.AddressBar.text())  # 获取文件对象,从系统开始文件夹开始递归搜索
            if targetfolder is not None:
                targetfolder.create_folder(file_name, self.FileSys.disk)
                QtWidgets.QMessageBox.information(None, '创建文件夹', '文件夹创建成功！')
                self.recover_table()
            else:
                QtWidgets.QMessageBox.warning(None, '创建文件夹', f'创建文件夹失败:找不到父文件夹')

    # 删除文件或文件夹
    def delete_ob(self):
        targetfolder = self.search_ob(self.FileSys, self.AddressBar.text())  # 获取文件对象,从系统开始文件夹开始递归搜索
        if targetfolder is not None:
            selecteditem = self.tableWidget.selectedItems()[0].text()  # 获取文件名
            _, file_ext = os.path.splitext(selecteditem)
            if file_ext == '':
                targetfolder.delete_folder(selecteditem, self.FileSys.disk)
                self.recover_table()
            else:
                targetfolder.delete_file(selecteditem, self.FileSys.disk)
                self.recover_table()
        else:
            QtWidgets.QMessageBox.information(None, '删除', '未知问题！未找到目标对象的父文件夹')

    # 显示属性
    def show_attributes(self):
        if self.tableWidget.selectedItems() != []:
            selecteditem = self.search_ob(self.FileSys, self.AddressBar.text()
                                          + self.tableWidget.selectedItems()[0].text())  # 获取文件
        else:
            selecteditem = self.search_ob(self.FileSys, self.AddressBar.text())  # 获取文件
        if selecteditem is None:
            return
        mid_name = selecteditem.get_name()
        mid_path = selecteditem.get_path()
        mid_size = str(selecteditem.get_space() / 1024) + "KB"
        mid_ctime = None
        mid_mtime = None
        mid_atime = None
        _, mid_type = os.path.splitext(selecteditem.get_name())
        if mid_type == "":
            mid_type = "文件夹"
        else:
            mid_ctime = datetime.fromtimestamp(int(os.path.getctime(mid_path + mid_name))).strftime("%Y-%m-%d %H:%M:%S")
            mid_mtime = datetime.fromtimestamp(int(os.path.getmtime(mid_path + mid_name))).strftime("%Y-%m-%d %H:%M:%S")
            mid_atime = datetime.fromtimestamp(int(os.path.getatime(mid_path + mid_name))).strftime("%Y-%m-%d %H:%M:%S")

        qdialog = QtWidgets.QDialog()
        qdialog.move(QtGui.QCursor.pos().x() + 30, QtGui.QCursor.pos().y() + 30)
        qdialog.resize(400, 500)
        qdialog.setWindowTitle(mid_name + u"属性")
        # 创建一个 QTabWidget 控件
        tab_widget = QtWidgets.QTabWidget()
        tab_widget.setMovable(True)

        # 创建并添加属性页
        tab = QtWidgets.QWidget()
        tab1 = QtWidgets.QWidget()
        tab2 = QtWidgets.QWidget()
        tab3 = QtWidgets.QWidget()
        tab_widget.addTab(tab, "常规")
        tab_widget.addTab(tab1, "安全")
        tab_widget.addTab(tab2, "详细信息")
        tab_widget.addTab(tab3, "以前的版本")
        # 属性页的信息(这里只用到常规页)
        vlayout = QtWidgets.QVBoxLayout(tab)
        label1 = QtWidgets.QLabel("文件类型：\t" + mid_type)
        label2 = QtWidgets.QLabel("路径：\t" + mid_path)
        label3 = QtWidgets.QLabel("大小：\t" + mid_size)
        vlayout.addWidget(label1)
        vlayout.addWidget(label2)
        vlayout.addWidget(label3)
        if mid_type != "文件夹":
            label4 = QtWidgets.QLabel("创建时间：\t" + mid_ctime)
            label5 = QtWidgets.QLabel("修改时间：\t" + mid_mtime)
            label6 = QtWidgets.QLabel("访问时间：\t" + mid_atime)
            vlayout.addWidget(label4)
            vlayout.addWidget(label5)
            vlayout.addWidget(label6)
        else:
            label7 = QtWidgets.QLabel("文件总数（含文件夹）：\t" + str(selecteditem.get_filenum()))
            vlayout.addWidget(label7)

        # 将属性页添加到弹窗中
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tab_widget)
        qdialog.setLayout(layout)

        # 显示弹窗
        qdialog.exec_()

    # 格式化
    def format(self):
        # 删除本地的文件多余文件
        for i in self.FileSys.folderList:
            shutil.rmtree(i.folderPath + i.folderName + '/')  # 删除本地的内容
        for j in self.FileSys.fileList:
            os.remove(j.filePath + j.fileName)  # 删除本地的文件

        # 读取pickle文件
        with open("./Fengye7_FileSystem/format_disk.pickle", 'rb') as f1:
            disk_data_pickle = pickle.load(f1)
        # 写入到另一个pickle文件
        with open("./Fengye7_FileSystem/disk.pickle", 'wb') as f2:
            pickle.dump(disk_data_pickle, f2)
        # 同时修改副本方便查看
        with open("./Fengye7_FileSystem/format_disk.txt", 'r') as f3:
            disk_data_txt = f3.read()
        with open("./Fengye7_FileSystem/disk.txt", 'w') as f4:
            f4.write(disk_data_txt)
        # ***********************同样的下面格式化目录****************
        with open("./Fengye7_FileSystem/format_directory.pickle", 'rb') as f5:
            directory_data_pickle = pickle.load(f5)
        # 写入到另一个pickle文件
        with open("./Fengye7_FileSystem/directory.pickle", 'wb') as f6:
            pickle.dump(directory_data_pickle, f6)
        # 同时修改副本方便查看
        with open("./Fengye7_FileSystem/format_directory.txt", 'r') as f7:
            directory_data_txt = f7.read()
        with open("./Fengye7_FileSystem/directory.txt", 'w') as f8:
            f8.write(directory_data_txt)
        QtWidgets.QMessageBox.information(None, '格式化', '格式化完毕！下面自动关闭，请重启！')
        QtCore.QCoreApplication.exit()

    # 重命名
    def rename_ob(self):
        targetfolder = self.search_ob(self.FileSys, self.AddressBar.text())  # 获取文件对象,从系统开始文件夹开始递归搜索
        if targetfolder is not None:
            selecteditem = self.tableWidget.selectedItems()[0].text()  # 获取文件名
            _, file_ext = os.path.splitext(selecteditem)
            # 弹出一个输入对话框，让用户输入新文件夹名称
            new_name, ok = QtWidgets.QInputDialog.getText(None, '重命名', '请输入新名称：')
            if ok:
                if file_ext == "":
                    targetfolder.rename_folder(selecteditem, new_name)
                else:
                    targetfolder.rename_file(selecteditem, new_name)
                self.recover_table()
        else:
            QtWidgets.QMessageBox.information(None, '删除', '未知问题！未找到目标对象的父文件夹')

    # 展示文件列表
    def show_table(self, folder):
        # 处理地址栏
        self.AddressBar.setText(folder.folderPath + folder.folderName + '/')
        # 优先展示文件夹
        if len(folder.folderList) != 0:
            for i in folder.folderList:
                self.tableWidget.insertRow(self.tableWidget.rowCount())  # 添加行
                newItem = QtWidgets.QTableWidgetItem(QtGui.QIcon("./imags/folder.jpg"), i.folderName)
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, newItem)

                midtime = datetime.fromtimestamp(int(os.path.getmtime(i.folderPath)))
                strtime = midtime.strftime("%Y-%m-%d %H:%M:%S")
                newtime = QtWidgets.QTableWidgetItem(strtime)
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, newtime)

                newtype = QtWidgets.QTableWidgetItem("文件夹")
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 2, newtype)

                newsize = QtWidgets.QTableWidgetItem(str(i.get_space() / 1024) + "KB")
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 3, newsize)
        # 列出文件
        if len(folder.fileList) != 0:
            for i in folder.fileList:
                self.tableWidget.insertRow(self.tableWidget.rowCount())  # 添加行
                _, file_ext = os.path.splitext(i.fileName)
                try:
                    newItem = QtWidgets.QTableWidgetItem(QtGui.QIcon("./imags/" + file_ext + ".png"), i.fileName)
                except:
                    newItem = QtWidgets.QTableWidgetItem(QtGui.QIcon("./imags/.txt.png"), i.fileName)  # 其他没有提供图标的文件类型
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, newItem)

                midtime = datetime.fromtimestamp(int(os.path.getmtime(i.filePath)))
                strtime = midtime.strftime("%Y-%m-%d %H:%M:%S")
                newtime = QtWidgets.QTableWidgetItem(strtime)
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, newtime)

                _, file_ext = os.path.splitext(i.fileName)
                newtype = QtWidgets.QTableWidgetItem(file_ext + "文件")
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 2, newtype)

                newsize = QtWidgets.QTableWidgetItem(str(i.get_space() / 1024) + "KB")
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 3, newsize)
        # 若文件夹为空
        if len(folder.folderList) == 0 and len(folder.fileList) == 0:
            self.tableWidget.insertRow(self.tableWidget.rowCount())  # 添加行
            newItem = QtWidgets.QTableWidgetItem("此文件夹为空。")
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, newItem)
        # 处理下框显示
        self.item_num_label.setText(str(folder.get_filenum()))
        self.selected_item_num.setText("选中0个项目")
        self.selected_item_size.setText("0KB")

    # 展示目录
    def show_list(self, tree, mid_list, mid_type):  # 这里原来是想文件数上展示文件夹和文件的，用mid_type区分操作,现摒弃
        if mid_type == Type.Folder:
            for i in mid_list:
                newItem = QtWidgets.QTreeWidgetItem()
                newItem.setText(0, i.folderName)
                newItem.setIcon(0, QtGui.QIcon("./imags/folder.jpg"))
                for j in i.folderList:
                    childItem = QtWidgets.QTreeWidgetItem()
                    childItem.setText(0, j.folderName)
                    childItem.setIcon(0, QtGui.QIcon("./imags/folder.jpg"))
                    newItem.addChild(childItem)
                    if len(j.folderList) != 0:
                        self.show_list(childItem, j.folderList, Type.Folder)
                    # if len(j.fileList) != 0:
                    #     self.show_list(childItem, j.fileList, Type.File)
                tree.addTopLevelItem(newItem)
                # for j in i.fileList:
                #     childItem = QtWidgets.QTreeWidgetItem()
                #     childItem.setText(0, j.fileName)
                #     childItem.setIcon(0, QtGui.QIcon("./imags/file.jpg"))
                #     newItem.addChild(childItem)
        # if mid_type == Type.File:
        #     for i in mid_list:
        #         newItem = QtWidgets.QTreeWidgetItem()
        #         newItem.setText(0, i.fileName)
        #         newItem.setIcon(0, QtGui.QIcon("./imags/file.jpg"))
        #         tree.addTopLevelItem(newItem)

    # 处理列表双击事件
    def enter_item(self):
        selecteditem = self.tableWidget.selectedItems()[0].text()  # 获取文件名
        _, file_ext = os.path.splitext(selecteditem)
        # 双击文件夹
        if file_ext == "":
            targetfolder = self.search_ob(self.FileSys,
                                          self.AddressBar.text() + selecteditem)  # 获取文件对象,从系统开始文件夹开始递归搜索
            if targetfolder is not None:
                self.tableWidget.setRowCount(0)  # 清空列表行
                self.tableWidget.clearContents()  # 清空内容
                self.show_table(targetfolder)  # 展示新位置
            else:
                QtWidgets.QMessageBox.information(None, 'error', '可能的情况：\n' +
                                                  '*该对象是无后缀名的文件，暂不支持打开！\n' +
                                                  '* 未查找到相关的文件夹')
        # 双击文件
        else:
            targetfile = self.search_ob(self.FileSys, self.AddressBar.text() + selecteditem)
            if targetfile is not None:
                self.on_modified(targetfile)

    # 监听文件保存
    class Monitor:
        def __init__(self, father, targetfile):
            self.father = father
            self.targetfile = targetfile

        class OnCloseHandler(PatternMatchingEventHandler):
            def __init__(self, father):
                """
                内部类初始化函数，构造时自动调用
                :param father: 外部类的实例对象
                """
                self.father = father

            def dispatch(self, event):
                print(event.event_type)
                if event.event_type == 'modified':
                    self.on_modified(event)

            def on_modified(self, event):
                if event.src_path == self.father.targetfile.filePath + self.father.targetfile.fileName:
                    new_data = self.father.targetfile.get_data()
                    # 每次文件更改需要调整文件占用的整个簇链，因为可能大小不变，内容变了
                    start_cluster = self.father.father.disk[self.father.targetfile.start_cluster]
                    end_cluster = self.father.father.disk[self.father.targetfile.end_cluster]
                    mid_cluster = start_cluster
                    mid_len = len(new_data)
                    while True:
                        if mid_len > 1024:
                            mid_cluster["size"] = 0
                            mid_cluster["data"] = new_data[:1024]  # 字符串的切片
                            new_data = new_data[1024:]
                            mid_len = len(new_data)
                            if mid_cluster["next"] is not None and mid_cluster != end_cluster:
                                mid_cluster = self.father.father.disk[mid_cluster["next"]]
                            else:
                                break
                        else:
                            mid_cluster["size"] = 1024 - mid_len
                            mid_cluster["data"] = new_data
                            new_data = None
                            mid_len = 0
                            break
                    if mid_cluster != end_cluster:  # 这种情况就是文件变小了，将后面的释放
                        mid_cluster["next"] = end_cluster["next"]  # 重连簇链，下面释放空间
                        while mid_cluster != self.father.father.disk[end_cluster["next"]]:
                            mid_cluster["data"] = None
                            mid_cluster["status"] = "free"
                            mid_cluster["size"] = 1024
                            mid_id = mid_cluster["next"]
                            mid_cluster["next"] = None
                            mid_cluster = self.father.father.disk[mid_id]
                    else:  # 这种情况就是文件扩大或不变
                        while mid_len > 0:
                            # 计算空间，只要还有空闲簇都能创建，空文件占用一个簇，当该文件文件输入内容超过该簇后，申请新簇，直到没有空闲簇
                            cluster_id = None
                            for i in self.father.father.disk:
                                if i["status"] == "free":
                                    cluster_id = i["cluster_id"]
                                    break
                            mid_id = end_cluster["next"]
                            end_cluster["next"] = cluster_id
                            self.father.father.disk[cluster_id]["next"] = mid_id  # 这三行在原来的簇链中插入新簇
                            self.father.father.disk[cluster_id]["status"] = "busy"  # 表示次簇已被使用
                            if mid_len > 1024:
                                self.father.father.disk[cluster_id]["size"] = 0
                                self.father.father.disk[cluster_id]["data"] = new_data[:1024]  # 字符串的切片
                                new_data = new_data[1024:]
                                mid_len = len(new_data)
                            else:
                                self.father.father.disk[cluster_id]["size"] = 1024 - mid_len
                                self.father.father.disk[cluster_id]["data"] = new_data
                                new_data = None
                                mid_len = 0
                                break

    # 处理文件外部打开用于读写，关闭后写入磁盘
    def on_modified(self, targetfile):
        # 监听文件关闭
        handler = self.Monitor(self.FileSys, targetfile)
        observer = Observer()
        observer.schedule(handler.OnCloseHandler(handler), path=targetfile.filePath, recursive=False)
        observer.start()
        targetfile.open_file()

    # 处理目录树点击事件
    def enter_list(self):
        selecteditem = self.treeWidget.selectedItems()[0].text(0)  # 获取文件对应的节点
        _, file_ext = os.path.splitext(selecteditem)
        # 点击文件夹
        if file_ext == "":
            targetpath = self.getpath(self.treeWidget.currentItem())
            targetfolder = self.search_ob(self.FileSys, targetpath)
            if targetfolder is not None:
                self.tableWidget.setRowCount(0)  # 清空列表行
                self.tableWidget.clearContents()  # 清空内容
                self.show_table(targetfolder)  # 展示新位置

    # 目录树从一个节点获取路径
    def getpath(self, item):
        if item.parent():
            temp = item.text(0)
            parent = self.getpath(item.parent())  # 递归获取完整路径
            if parent is not None:
                res = os.path.join(parent, temp)
                return res
            else:
                return temp
        else:
            return "./Fengye7_FileSystem/" + item.text(0) + '/'

    # 处理页面跳转
    def jump_path(self):
        tagetfolder = self.search_ob(self.FileSys,
                                     self.AddressBar.text())  # 获取文件对象,从系统开始文件夹开始递归搜索
        if tagetfolder is not None:
            self.tableWidget.setRowCount(0)  # 清空列表行
            self.tableWidget.clearContents()  # 清空内容
            self.show_table(tagetfolder)  # 展示新位置
        else:
            QtWidgets.QMessageBox.warning(None, '跳转',
                                          f'跳转失败！目标目录不存在。\n请点击目录刷新地址栏信息，以便其他操作！！！')

    # 搜索路径对应的文件对象
    def search_ob(self, folder, path):
        if path == './Fengye7_FileSystem/':
            return self.FileSys
        _, file_ext = os.path.splitext(path)
        if file_ext == "":
            if len(folder.folderList) != 0:
                answer = None
                for i in folder.folderList:
                    if i.folderPath + i.folderName == path or i.folderPath + i.folderName + '/' == path:
                        # print(i.folderName)测试是否找到
                        answer = i
                    if len(i.folderList) != 0 and answer is None:  # 没有搜索到则继续进入子文件夹搜索
                        answer = self.search_ob(i, path)
                    if answer is not None:
                        break
                return answer
            else:  # 查询到底
                return None
        else:  # 此种情况应该是查找文件
            if len(folder.fileList) != 0:
                answer = None
                for i in folder.fileList:
                    if i.filePath + i.fileName == path:
                        answer = i
                if len(folder.folderList) != 0 and answer is None:
                    for j in folder.folderList:
                        answer = self.search_ob(j, path)
                        if answer is not None:
                            break
                return answer
            else:
                return None


import sys

if __name__ == '__main__':
    # 适配2k高分辨率屏幕
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()  # 创建窗体对象
    ui = Ui_Fengye7_FileSystem(MainWindow)  # 创建PyQt设计的窗体对象
    MainWindow.show()  # 显示窗体
    sys.exit(app.exec_())  # 程序关闭时退出进程
