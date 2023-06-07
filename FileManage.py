from Folder import *
import pickle


class FileManage(Folder):  # 用于创建一个系统，实际也就是一个文件夹
    def __init__(self, path, name):
        # 磁盘——管理文件:创建一个模拟磁盘，包含512个簇(0-511)，簇大小为1024B(4KB)，簇中记录数据
        self.disk = [{"cluster_id": id, "size": 1024, "data": None, "status": "free", "next": None} for id in
                     range(512)]
        # 读入磁盘
        if os.path.exists(path + name + '/' + 'disk.pickle'):
            with open(path + name + '/' + 'disk.pickle', 'rb') as f:
                mid_disk = pickle.load(f)
            for cluster in mid_disk:
                self.disk[cluster["cluster_id"]]["size"] = cluster["size"]
                self.disk[cluster["cluster_id"]]["data"] = cluster["data"]
                self.disk[cluster["cluster_id"]]["status"] = cluster["status"]
                self.disk[cluster["cluster_id"]]["next"] = cluster["next"]

        # 文件夹属性，相当于一个目录结构
        self.folderName = name
        self.folderPath = path
        super().__init__(path, name)
        self.fileList = []  # 文件夹中包含的文件
        self.folderList = []  # 文件夹中包含的文件夹
        # 读入目录
        if os.path.exists(path + name + '/' + 'directory.pickle'):
            with open(path + name + '/' + 'directory.pickle', 'rb') as f:
                mid_directory = pickle.load(f)

            def deserialize_file(directory):
                filePath = directory['path']
                fileName = directory['name']
                file = File(filePath, fileName)
                file.start_cluster = directory['start_cluster']
                file.end_cluster = directory['end_cluster']
                # 文件写入磁盘上的内容
                start_cluster = self.disk[file.start_cluster]
                end_cluster = self.disk[file.end_cluster]
                mid_cluster = start_cluster
                while True:
                    if mid_cluster["data"] is not None:
                        file.write_data(mid_cluster["data"])
                    if mid_cluster["next"] is not None and mid_cluster != end_cluster:
                        mid_cluster = self.FileSys.disk[mid_cluster["next"]]
                    else:
                        break
                return file

            def deserialize_folder(directory):
                folderPath = directory['path']
                folderName = directory['name']
                folder = Folder(folderPath, folderName)
                folder.fileList = [deserialize_file(f) for f in directory['file_list']]
                folder.folderList = [deserialize_folder(f) for f in directory['folder_list']]
                folder.start_cluster = directory['start_cluster']
                folder.end_cluster = directory['end_cluster']
                return folder

            midfolder = deserialize_folder(mid_directory)
            self.folderName = midfolder.folderName
            self.folderPath = midfolder.folderPath
            self.fileList = midfolder.fileList
            self.folderList = midfolder.folderList
            self.start_cluster = midfolder.start_cluster
            self.end_cluster = midfolder.end_cluster

        # # 预先创建几个文件夹，文件夹中也创建几个文件
        # self.create_folder("folder1", self.disk)
        # self.folderList[0].create_file("file1.txt", self.disk)
        # self.folderList[0].create_file("file2.txt", self.disk)
        # self.folderList[0].create_file("file3.txt", self.disk)
        # self.folderList[0].create_folder("sub_folder1", self.disk)
        # self.folderList[0].create_folder("sub_folder2", self.disk)
        #
        # self.create_folder("folder2", self.disk)
        # self.create_folder("folder3", self.disk)
        #
        # self.create_folder("folder4", self.disk)
        # self.folderList[3].create_file("file1.c", self.disk)
        # self.folderList[3].create_file("file2.h", self.disk)
        # self.folderList[3].create_folder("sub_folder1", self.disk)
        #
        # self.create_folder("folder5", self.disk)
        #
        # self.create_file("file1.txt", self.disk)
        # self.create_file("file2.txt", self.disk)
