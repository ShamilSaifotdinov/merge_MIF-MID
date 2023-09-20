from osgeo import ogr, osr
import re, os, zipfile, io, tempfile
import traceback

from .TempFile import TempFile
from .MergeGeoms import MergeGeoms

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

class MergeFeatures:
    # MIF file contains mif and mid format files
    mif_merge = "/result/result.mif"   # Go ahead with 9
    mid_merge = "/result/result.mid"   # Empty text

    def __init__(self, result, protocol):
        self.protocol = protocol
        self.mif_merge = result + self.mif_merge
        self.mid_merge = result + self.mid_merge        
        
        # Create result folder
        os.makedirs(os.path.dirname(self.mif_merge), exist_ok=True)
        
        self.mif = open(self.mif_merge, "w")
        self.mid = open(self.mid_merge, "w")
        
        self.mif.writelines(header)
        self.protocol("Add Header")

        # self.openZip(file, mif, mid)

        # for mifSrc in filesList:
        #     # Processing each MIF file
        #     if mifSrc.endswith('.mif'):
        #         openMIF(folder + mifSrc, mif, mid)

    def writeMif(self, fileName):
        srcMif = open(fileName, "rt").readlines()
        
        # Read all mif, mid files
        # cnt_result = [0, 0]
        
        # mif file line write txt
        isHeader = True
        for line in srcMif:
            # print('line[:-1]'+line[:-1])
            # print(line)
            if not(isHeader):
                self.mif.write(line)
                # cnt_result[0] += 1

            if isHeader:
                x = re.search('^Data', line)

            if x:
                isHeader = False
        # print('\t' + 'MIF: write ' + str(cnt_result[0]) + ' OK!')

    # def openMIF(self, srcMif, mif, mid):
    def processMifMid(self, srcMif, midPath):
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
                    self.mif.write("Collection " + str(count))
                self.mid.write("\"" + obj_KN + "\"\r")
                self.writeMif(temp.tempMif)

                temp.delete()
                
            else:
                self.protocol(srcMif + " - найдена сторонняя графика")
                
            srcLayer.ResetReading()

        except Exception:
            print(traceback.format_exc())
            self.protocol(srcMif + ":\n")
            self.protocol(traceback.format_exc())

    """def openZip(self, zip, mif, mid):
        archive = zipfile.ZipFile(zip)
        members = archive.namelist()            

        for member in members:
            # We have a zip within a zip
            #print(io.BytesIO(archive.read(member)))
            if  member.endswith('.zip'):
                print("\n" + member + ' - ZIP:')
                # print(io.BytesIO(archive.read(member)))
                self.openZip(io.BytesIO(archive.read(member)), mif, mid)
            
            if member.endswith('.mif'):
                with tempfile.TemporaryDirectory() as tempdir:
                    archive.extract(member, tempdir)
                    filename = os.path.splitext(member)[0]
                    try:
                        archive.extract(filename + ".mid", tempdir)
                    except:
                        print(": Отсутствует " + filename + ".mid")
                    else: 
                        self.openMIF(tempdir + "/" + member, mif, mid)
                    # archive.open(filename + ".mid")
                    # print(filename + ":")
    """

    def completeMerge(self):
        self.mif.close()
        self.mid.close()

# if __name__ == '__main__':
#     # Processing source files
#     # file = "borders_geodata_86.zip"
#     file = "merge/86_02-15p1.zip"

#     # # Processing source files
#     folder = 'merge/86_02-15p1/'
#     # # folder = 'borders_geodata_86(2)/'
#     # # mifSrc = "collection.mif"

#     # # filesList = os.listdir(folder)
#     filesList = ['collection.mif']
#     MergeFeatures()