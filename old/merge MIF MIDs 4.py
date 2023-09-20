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

def openZip(zip):
    cnt_result = [0, 0]

    archive = zipfile.ZipFile(zip)
    members = archive.namelist()            

    for member in members:
        # We have a zip within a zip
        #print(io.BytesIO(archive.read(member)))
        if '.zip' in member:
            print()
            print(member + ' - ZIP:')
            cnt = openZip(io.BytesIO(archive.read(member)))
        else:
            write_txt_ls = io.TextIOWrapper(archive.open(member)).readlines()
            cnt = writeMifMid(member, write_txt_ls)

        cnt_result[0] += cnt[0]
        cnt_result[1] += cnt[1]
    
    return cnt_result

def writeMifMid(name_file, lines):
    global f_mif, f_mid, mif_file, mid_file

    # Read all mif, mid files
    # print(file)
    cnt_result = [0, 0]
    
    # mif file line write txt
    if'.mif' in name_file:
        mif_file += 1
        isHeader = True
        for line in lines:
            # print('line[:-1]'+line[:-1])

            if not(isHeader):
                f_mif.write(line)
                cnt_result[0] += 1

            if isHeader:
                x = re.search('^Data', line)

            if x:
                isHeader = False
        print(name_file + ': write ' + str(cnt_result[0]) + ' OK!')

    # mid file line write txt
    if'.mid' in name_file:
        mid_file += 1
        for line in lines:
            f_mid.write(line)
            cnt_result[1] += 1
            # print("mid:"+line)
        print(name_file + ': write ' + str(cnt_result[1]) + ' OK!')
    
    return cnt_result

# MIF file contains mif and mid format files
MIF_path = "C:/Practice/Python/merge mif mids/mm/"          # Folder with MIF's
mif_merge = "C:/Practice/Python/merge mif mids/merge.mif"   # Go ahead with 9
mid_merge = "C:/Practice/Python/merge mif mids/merge.mid"   # Empty text

# mif, number of files written by mid
mif_file = 0
mid_file = 0

# mif, mid write line number
sum_mif = 0
sum_mid = 0

MIF_ls = os.listdir(MIF_path)
print(MIF_ls)
print()

# Write mif and mid txt files separately
f_mif = open(mif_merge, "a")  # Additional writing mode
f_mid = open(mid_merge, "a")

for line in header:
    f_mif.write(line)

for file in MIF_ls:
    cnt_result = [0, 0]
    if'.zip' in file:
        print()
        print(file + ' - ZIP:')
        cnt_result = openZip(MIF_path + file)

        print()
    else:
        f1 = open(MIF_path + file, "rt")
        write_txt_ls = f1.readlines()
        # print(write_txt_ls)

        cnt_result = writeMifMid(file, write_txt_ls)
        
        # Close file
        f1.close()

    # Record the total number of lines written in mif, mid
    sum_mif += cnt_result[0]
    sum_mid += cnt_result[1]

print()
# mif Number of files written, total number of lines written
print("MIF merge OK!"+' Write a total of ' + str(mif_file) + ' file! ' + str(sum_mif) + ' OK!')

# mid Number of files written, total number of lines written
print("MID merge OK!"+' Write a total of ' + str(mid_file) + ' file! ' + str(sum_mid) + ' OK!')

f_mif.close()
f_mid.close()