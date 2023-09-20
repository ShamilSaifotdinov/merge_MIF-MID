from osgeo import ogr
# import ogr2ogr
import re, zipfile, io, os, tempfile

class createTempFile:
    tempFile = "temp.mif"

    def __init__(self, obj_KN, geomcol):

        self.tempDriver = ogr.GetDriverByName("MapInfo File")
        tempSource = self.tempDriver.CreateDataSource(self.tempFile)
        self.tempLayer = tempSource.CreateLayer("temp")

        idField = ogr.FieldDefn("NOTE", ogr.OFTString)
        self.tempLayer.CreateField(idField)

        newFeature = ogr.Feature(self.tempLayer.GetLayerDefn())
        newFeature.SetGeometry(geomcol)
        newFeature.SetField("NOTE", obj_KN)
        self.tempLayer.CreateFeature(newFeature)
        
        print(obj_KN + " Geometry: " + str(newFeature.GetGeometryRef().GetGeometryCount()), end = ' ')
    
    def delete(self):
        self.tempDriver.DeleteDataSource(self.tempFile)

def writeMif(outMif, fileName):
    srcMif = open(fileName + ".mif", "rt").readlines()
    
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

def addMultiGeometry(srcGeom, outGeom):
    for i in range(0, srcGeom.GetGeometryCount()):
        outGeom.AddGeometry(srcGeom.GetGeometryRef(i))    
    # print("Стало " + outGeom.GetGeometryName() + ": " + str(outGeom.GetGeometryCount()))

def mergeGeometries(srcLayer):
    geomPolygon = ogr.Geometry(ogr.wkbMultiPolygon)
    geomPolyline = ogr.Geometry(ogr.wkbMultiLineString)
    geomMultiPoint = ogr.Geometry(ogr.wkbMultiPoint)

    geomcol =  ogr.Geometry(ogr.wkbGeometryCollection)

    for feature in srcLayer:
        geometry = feature.GetGeometryRef()
        geoType = geometry.GetGeometryType()

        # print("\nТип геометрии: " + geometry.GetGeometryName())

        if geoType == ogr.wkbPolygon:       geomPolygon.AddGeometry(geometry)
        elif geoType == ogr.wkbLineString:  geomPolyline.AddGeometry(geometry)
        # elif geoType == ogr.wkbPoint:       geomMultiPoint.AddGeometry(geometry)
        
        elif geoType == ogr.wkbMultiPolygon:    addMultiGeometry(geometry, geomPolygon)
        elif geoType == ogr.wkbMultiLineString: addMultiGeometry(geometry, geomPolyline)
        # elif geoType == ogr.wkbMultiPoint:      addMultiGeometry(geometry, geomMultiPoint)
        
        elif geoType == ogr.wkbGeometryCollection:
            for i in range(0, geometry.GetGeometryCount()):
                g = geometry.GetGeometryRef(i)
                gType = g.GetGeometryType()

                # print("Тип вложенной геометрии: " + g.GetGeometryName())

                if gType == ogr.wkbPolygon:         geomPolygon.AddGeometry(g)
                elif gType == ogr.wkbLineString:    geomPolyline.AddGeometry(g)
                # elif gType == ogr.wkbPoint:         geomMultiPoint.AddGeometry(g)

                elif gType == ogr.wkbMultiPolygon:    addMultiGeometry(g, geomPolygon)
                elif gType == ogr.wkbMultiLineString: addMultiGeometry(g, geomPolyline)
                # elif gType == ogr.wkbMultiPoint:      addMultiGeometry(g, geomMultiPoint)
                
                else: print("No geometry")
        else: print("No geometry")

        # print("Количество полигонов: " + str(geomPolygon.GetGeometryCount()))
        # print("Количество полилиний: " + str(geomPolyline.GetGeometryCount()))
        # print("Количество точек: " + str(geomMultiPoint.GetGeometryCount()))
    
    # print(geomPolygon.GetGeometryCount())
    # print(geomPolyline.GetGeometryCount())
    # print(geomMultiPoint.GetGeometryCount())
    
    if geomPolygon.GetGeometryCount():      geomcol.AddGeometry(geomPolygon)
    if geomPolyline.GetGeometryCount():     geomcol.AddGeometry(geomPolyline)
    if geomMultiPoint.GetGeometryCount():   geomcol.AddGeometry(geomMultiPoint)
    print("Add: " + feature.GetField("NOTE") + " Count: " + str(feature.GetGeometryRef().GetGeometryCount()))

    return geomcol

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

def openMIF(srcMif, mif, mid):
    dataSource = ogr.Open(srcMif, 0)
    srcLayer = dataSource.GetLayer()

    obj_KN = srcLayer.GetFeature(1).GetField("NOTE")
    srcLayer.SetAttributeFilter(f"NOTE != '{obj_KN}'")
    # print("Объект: " + obj_KN)
    if srcLayer.GetFeatureCount() == 0:
        srcLayer.SetAttributeFilter("")

        # Merge all geometries from layer in one geometry
        geomcol = mergeGeometries(srcLayer)
        
        # create temp file
        temp = createTempFile(obj_KN, geomcol)
        
        # count of objs
        # open file in read mode
        with open("temp.mid", 'r') as fp:
            for count, line in enumerate(fp):
                pass
        print('Total Lines:', count + 1)

        # Add feature in result layer
        if count:
            mif.write("Collection " + str(count + 1))
        mid.write("\"" + obj_KN + "\"\r")
        writeMif(mif, "temp")

        temp.delete()
        
    else:
        # print(mifSrc + " - найдена сторонняя графика")
        print(obj_KN + " - найдена сторонняя графика")
        
    srcLayer.ResetReading()

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
    mif = open(resultFile + ".mif", "a")
    mid = open(resultFile + ".mid", "a")
    mif.writelines(header)

    # Processing source files
    # file = "borders_geodata_86.zip"
    file = "86_02-15p1.zip"

    openZip(file, mif, mid)

    mif.close()
    mid.close()