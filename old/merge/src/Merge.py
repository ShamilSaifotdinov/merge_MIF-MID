from osgeo import ogr, osr
import re, os, zipfile, io, tempfile
import traceback

from TempFile import TempFile
from MergeGeoms import MergeGeoms

def writeMif(outMif, fileName):
    srcMif = open(fileName, "rt").readlines()
    
    # Read all mif, mid files
    # cnt_result = [0, 0]
    
    # mif file line write txt
    isHeader = True
    for line in srcMif:
        # print('line[:-1]'+line[:-1])
        # print(line)
        if not(isHeader):
            outMif.write(line)
            # cnt_result[0] += 1

        if isHeader:
            x = re.search('^Data', line)

        if x:
            isHeader = False
    # print('\t' + 'MIF: write ' + str(cnt_result[0]) + ' OK!')

def openMIF(srcMif, mif, mid):
    try:
        dataSource = ogr.Open(srcMif, 0)
        srcLayer = dataSource.GetLayer()

        obj_KN = srcLayer.GetFeature(1).GetField("NOTE")
        srcLayer.SetAttributeFilter(f"NOTE != '{obj_KN}'")
        # print("Объект: " + obj_KN)
        if srcLayer.GetFeatureCount() == 0:
            srcLayer.SetAttributeFilter("")

            # Merge all geometries from Layer to MultiPoint, MultiLineString and MultiPoint
            geomcol = MergeGeoms(srcLayer)
            
            # create temp file and add geometries
            temp = TempFile(obj_KN, geomcol)
            
            # count of objs
            count = temp.getCount()

            # Add feature in result layer
            if count > 1:
                mif.write("Collection " + str(count))
            mid.write("\"" + obj_KN + "\"\r")
            writeMif(mif, temp.tempMif)

            temp.delete()
            
        else:
            print(srcMif + " - найдена сторонняя графика")
            protocol.append(srcMif + ";\"найдена сторонняя графика\"\n")
            
        srcLayer.ResetReading()

    except Exception:
        print(traceback.format_exc())
        protocol.append(srcMif + ":\n")
        protocol.append(traceback.format_exc())

def openZip(zip, mif, mid):
    archive = zipfile.ZipFile(zip)
    members = archive.namelist()            

    for member in members:
        # We have a zip within a zip
        #print(io.BytesIO(archive.read(member)))
        if  member.endswith('.zip'):
            print("\n" + member + ' - ZIP:')
            # print(io.BytesIO(archive.read(member)))
            openZip(io.BytesIO(archive.read(member)), mif, mid)
        
        if member.endswith('.mif'):
            with tempfile.TemporaryDirectory() as tempdir:
                archive.extractall(tempdir)
                filename = os.path.splitext(member)[0]
                archive.open(filename + ".mid")
                # print(filename + ":")
                openMIF(tempdir + "/" + member, mif, mid)

if __name__ == '__main__':
    # Create result file
    resultFile = "result"

    header = [
        'Version 300\r',
        'Charset "WindowsCyrillic"\r',
        'Delimiter ","\r',
        'CoordSys NonEarth Units "m" Bounds (0, 0) (10000000, 10000000)\r',
        'Columns 1\r',
        '\tNOTE Char(254)\r',
        'Data\r',
        '\r'
        ]
    protocol = []
    
    mif = open(resultFile + ".mif", "w")
    mid = open(resultFile + ".mid", "w")
    mif.writelines(header)

    # Processing source files
    # file = "borders_geodata_86.zip"
    file = "86_02-15p1.zip"

    openZip(file, mif, mid)

    # # Processing source files
    # folder = '86_02-15p1/'
    # # folder = 'borders_geodata_86(2)/'
    # # mifSrc = "collection.mif"

    # # filesList = os.listdir(folder)
    # filesList = ['collection.mif']

    # for mifSrc in filesList:
    #     # Processing each MIF file
    #     if mifSrc.endswith('.mif'):
    #         openMIF(folder + mifSrc, mif, mid)

    mif.close()
    mid.close()
    with open("protocol.csv", "w") as csv:
        csv.writelines(protocol)
        csv.close()