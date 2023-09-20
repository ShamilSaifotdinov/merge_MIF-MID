from PyQt5.QtWidgets import *
import os, io, zipfile, tempfile
from MergeText import MergeText
from MergeFeatures import MergeFeatures

TextType = "Merge text"
FeaturesType = "Merge features"


class ProcessPaths:
    protocolCSV = []

    def __init__(self, gui, src, result, type=FeaturesType):
        self.gui = gui
        # +++ Check path +++
        
        if src in result:            
            QMessageBox.warning(None, "Внимание!", "Выберите папку для сохранения, не входящую в папку с MIF MID!")
            return
        if not src or not result:
            QMessageBox.warning(None, "Внимание!", "Выберите папку!")
            return
        
        if type == TextType: self.merge = MergeText(result, self.protocol)
        elif type == FeaturesType: self.merge = MergeFeatures(result, self.protocol)

        self.openFolder(src + "/")

        self.merge.completeMerge()
        with open("protocol.csv", "w") as csv:
            csv.writelines(self.protocolCSV)
            csv.close()

    def openFolder(self, path):
        files = [elem.lower() for elem in os.listdir(path)]
        self.protocol("\n" + str(files) + "\n")
        
        for file in files:
            if os.path.isdir(path + file):
                self.openFolder(path + file + "/")

            if file.endswith('.zip'):         
                self.protocol("\n" + file + ' - ZIP:')
                self.openZip(path + file)                
                self.protocol("")
            
            if file.endswith('.mif'):
                filename = os.path.splitext(file)[0]
                self.protocol(filename + ":")
                
                mid = filename + ".mid"
                if mid in files:
                    self.merge.processMifMid(path + file, path + mid)
                else:                    
                    self.protocol(path + ": Отсутствует " + mid)

    def openZip(self, zip):
        archive = zipfile.ZipFile(zip)
        members = archive.namelist()            

        for member in members:
            # We have a zip within a zip
            #print(io.BytesIO(archive.read(member)))
            if member.lower().endswith('.zip'):
                self.protocol("\n" + member + ' - ZIP:')
                arcBin = io.BytesIO(archive.read(member))
                arcBin.filename = member
                # print(arcBin)
                self.openZip(arcBin)
            
            if member.lower().endswith('.mif'):
                # filename = os.path.splitext(member)[0]
                # self.protocol(filename.encode('cp437').decode('cp866') + ":")
                
                # mid = filename + ".mid"
                # if mid in members:                    
                #     self.merge.writeMifMid(
                #         io.TextIOWrapper(archive.open(member)).readlines(), 
                #         io.TextIOWrapper(archive.open(mid)).readlines()
                #     )
                # else:
                #     self.protocol((zip if type(zip) is str else zip.filename) + ": Отсутствует " + mid.encode('cp437').decode('cp866'))

                with tempfile.TemporaryDirectory() as tempdir:
                    archive.extract(member, tempdir)
                    filename = os.path.splitext(member)[0]
                    self.protocol(filename.encode('cp437').decode('cp866') + ":")

                    mid = filename + ".mid"
                    try:
                        archive.extract(filename + ".mid", tempdir)
                    except:
                        self.protocol((zip if type(zip) is str else zip.filename) + ": Отсутствует " + mid.encode('cp437').decode('cp866'))
                    else: 
                        self.merge.processMifMid(tempdir + "/" + member,
                                               tempdir + "/" + mid)
            """
            else:
                write_txt_ls = io.TextIOWrapper(archive.open(member)).readlines()
                cnt = self.writeMifMid(member, write_txt_ls)

            cnt_result[0] += cnt[0]
            cnt_result[1] += cnt[1]
            """
    
    def protocol(self, message):
        print(message)
        self.gui(message)
        self.protocolCSV.append(message)