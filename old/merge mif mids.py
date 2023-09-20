# -*- coding: utf-8 -*-
# MIF format file merge-including reading and writing related counts
import os
import re
#import shutil

#city_ls = ['TIANJIN','XIANGGANG']
# MIF file contains mif and mid format files
MIF_path = "C:/Users/shami/OneDrive/Рабочий стол/АСКОН/5 Графический модуль/Тест/1988/Графика из РР/Графика из РР/"
mif_merge = "C:/result mif/mif_merge.mif"  # Go ahead with 9
mid_merge = "C:/result mif/mid_merge.mid"  # Empty text


MIF_ls = os.listdir(MIF_path)
# mif string to be skipped in the file
# forbid_txt = 'Version 300\
# Charset "Neutral"\
# Delimiter ","\
# ^CoordSys\
# Columns 3\
#   ID Integer\
#   LABEL Char(254)\
#   NOTE Char(254)\
# Data'
forbid_txt = [
    '^Version',
    '^Charset',
    '^Delimiter',
    '^CoordSys',
    '^Columns',
    'ID Integer',
    'LABEL Char.*',
    'NOTE Char.*',
    'Data'
]

# mif, mid write line number
sum_mif = 0
sum_mid = 0
# mif, number of files written by mid
mif_file = 0
mid_file = 0

def checkForbid(line):
    rgxFlag = False
    
    for rgx in forbid_txt:
        x = re.search(rgx, line)
        if x:
            rgxFlag = True
    
    return rgxFlag

for file in MIF_ls:
    # Read all mif, mid files
    # print(file)
    cnt_mif = 0
    cnt_mid = 0
    f1 = open(MIF_path + file, "rt")
    write_txt_ls = f1.readlines()
    # print(write_txt_ls)

    # Write mif and mid txt files separately
    f_mif = open(mif_merge, "a")  # Additional writing mode
    f_mid = open(mid_merge, "a")

    # mif file line write txt
    if'.mif' in file:
        mif_file += 1
        for line in write_txt_ls:
            # print('line[:-1]'+line[:-1])
            if  not(checkForbid(line)):  # ['Version 300\n','Charset "Neutral"\n'...]
                f_mif.write(line)
                cnt_mif += 1
                # print("mif:"+line)
            

        print(file + ': write ' + str(cnt_mif) + ' OK!')

    # mid file line write txt
    if'.mid' in file:
        mid_file += 1
        for line in write_txt_ls:
            f_mid.write(line)
            cnt_mid += 1
            # print("mid:"+line)
        print(file + ': write ' + str(cnt_mid) + ' OK!')

    # Record the total number of lines written in mif, mid
    sum_mif += cnt_mif
    sum_mid += cnt_mid

# Close file
f1.close()
f_mif.close()
f_mid.close()

# mif Number of files written, total number of lines written
print("MIF merge OK!"+' Write a total of ' +
      str(mif_file) + ' file! ' + str(sum_mif) + ' OK!')

# mid Number of files written, total number of lines written
print("MID merge OK!"+' Write a total of ' +
      str(mid_file) + ' file! ' + str(sum_mid) + ' OK!')