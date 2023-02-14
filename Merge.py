from PyQt5.QtWidgets import *

# -*- coding: utf-8 -*-
# MIF format file merge-including reading and writing related counts
import os
import re
import io
import zipfile

# Header of mif
header = [
    'Version 300\r',
    'Charset "WindowsCyrillic"\r',
    'Delimiter ","\r',
    'CoordSys NonEarth Units "m" Bounds (0, 0) (10000000, 10000000)\r',
    'Columns 3\r',
    '\tID Integer\r',
    '\tLABEL Char(254)\r',
    '\tNOTE Char(254)\r',
    'Data\r'
    ]

class Merge:
        # MIF file contains mif and mid format files
    MIF_path = "/"          # Folder with MIF's
    mif_merge = "/result/result.mif"   # Go ahead with 9
    mid_merge = "/result/result.mid"   # Empty text    

    # mif, number of files written by mid
    mif_file = 0
    mid_file = 0

    # mif, mid write line number
    sum_mif = 0
    sum_mid = 0

    f_mif = ''
    f_mid = ''

    def __init__(self, src, result, gui):
        """
        Check path
        """
        if src in result:            
            QMessageBox.warning(None, "Внимание!", "Выберите папку для сохранения, не входящую в папку с MIF MID!")
            return
        if not src or not result:
            QMessageBox.warning(None, "Внимание!", "Выберите папку!")
            return
        
        self.MIF_path = src + self.MIF_path
        self.mif_merge = result + self.mif_merge
        self.mid_merge = result + self.mid_merge

        self.gui = gui        
                
        """
        Start process
        """
        # Create result folder
        os.makedirs(os.path.dirname(self.mif_merge), exist_ok=True)
        
        # Write MIF and MID txt files separately
        self.f_mif = open(self.mif_merge, "a")  # Additional writing mode
        self.f_mid = open(self.mid_merge, "a")

        # Adding Header of MIF
        for line in header:
            self.f_mif.write(line)
        else:            
            self.protocol("Add Header")
        
        self.openFolder(self.MIF_path)
        
        self.f_mif.close()
        self.f_mid.close()

        """
        Result stat
        """
        self.protocol("")
        # mif Number of files written, total number of lines written
        self.protocol("MIF merge OK!"+' Write a total of ' + str(self.mif_file) + ' file! ' + str(self.sum_mif) + ' OK!')
        # mid Number of files written, total number of lines written
        self.protocol("MID merge OK!"+' Write a total of ' + str(self.mid_file) + ' file! ' + str(self.sum_mid) + ' OK!')

    def openFolder(self, path):
        files = os.listdir(path)
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
                    self.writeMifMid(
                        open(path + file, "rt"),
                        open(path + filename + ".mid", "rt"),
                    )
                else:                    
                    self.protocol(path + ": Отсутствует " + mid)

    def openZip(self, zip):
        archive = zipfile.ZipFile(zip)
        members = archive.namelist()            

        for member in members:
            # We have a zip within a zip
            #print(io.BytesIO(archive.read(member)))
            if  member.endswith('.zip'):
                self.protocol("\n" + member + ' - ZIP:')
                print(io.BytesIO(archive.read(member)))
                self.openZip(io.BytesIO(archive.read(member)))
            
            if member.endswith('.mif'):
                filename = os.path.splitext(member)[0]
                self.protocol(filename + ":")
                
                mid = filename + ".mid"
                if mid in members:                    
                    self.writeMifMid(
                        io.TextIOWrapper(archive.open(member)).readlines(), 
                        io.TextIOWrapper(archive.open(mid)).readlines()
                    )
                else:                    
                    self.protocol(zip + ": Отсутствует " + mid)
            
            """
            else:
                write_txt_ls = io.TextIOWrapper(archive.open(member)).readlines()
                cnt = self.writeMifMid(member, write_txt_ls)

            cnt_result[0] += cnt[0]
            cnt_result[1] += cnt[1]
            """
        
    """ writeMifMid
    
    def writeMifMid(self, name_file, lines):
        # Read all mif, mid files
        # print(file)
        cnt_result = [0, 0]
        
        # mif file line write txt
        if name_file.endswith('.mif'):
            self.mif_file += 1
            isHeader = True
            for line in lines:
                # print('line[:-1]'+line[:-1])

                if not(isHeader):
                    self.f_mif.write(line)
                    cnt_result[0] += 1

                if isHeader:
                    x = re.search('^Data', line)

                if x:
                    isHeader = False
            self.protocol(name_file + ': write ' + str(cnt_result[0]) + ' OK!')

        # mid file line write txt
        if name_file.endswith('.mid'):
            self.mid_file += 1
            for line in lines:
                self.f_mid.write(line)
                cnt_result[1] += 1
                # print("mid:"+line)
            
            self.protocol(name_file + ': write ' + str(cnt_result[1]) + ' OK!')
        
        return cnt_result
    """

    def writeMifMid(self, mif, mid):
        # Read all mif, mid files
        cnt_result = [0, 0]
        
        # mif file line write txt
        self.mif_file += 1
        isHeader = True
        for line in mif:
            # print('line[:-1]'+line[:-1])

            if not(isHeader):
                self.f_mif.write(line)
                cnt_result[0] += 1

            if isHeader:
                x = re.search('^Data', line)

            if x:
                isHeader = False
        self.protocol('\t' + 'MIF: write ' + str(cnt_result[0]) + ' OK!')
            
        # mid file line write txt
        self.mid_file += 1
        for line in mid:
            self.f_mid.write(line)
            cnt_result[1] += 1
            # print("mid:"+line)
        
        self.protocol('\t' + 'MID: write ' + str(cnt_result[1]) + ' OK!')        

        # Record the total number of lines written in mif, mid
        self.sum_mif += cnt_result[0]
        self.sum_mid += cnt_result[1]

    def protocol(self, message):
        print(message)
        self.gui(message)
