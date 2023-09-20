from osgeo import ogr, osr
# import ogr2ogr
import re, os
import traceback

class createTempFile:
    tempFile = "temp.mif"

    def __init__(self, obj_KN, geomcol):
        self.tempDriver = ogr.GetDriverByName("MapInfo File")
        tempSource = self.tempDriver.CreateDataSource(self.tempFile)
        self.tempLayer = tempSource.CreateLayer("temp")

        idField = ogr.FieldDefn("NOTE", ogr.OFTString)
        self.tempLayer.CreateField(idField)

        newFeature = ogr.Feature(self.tempLayer.GetLayerDefn())
        newFeature.SetGeometry(geomcol[0])
        newFeature.SetField("NOTE", obj_KN)
        self.tempLayer.CreateFeature(newFeature)
        
        countGeom = newFeature.GetGeometryRef().GetGeometryCount()

        if geomcol[1].GetGeometryCount():
            self.addMultiPoint(obj_KN, geomcol[1])
            countGeom += 1

        # print(newFeature.GetGeometryRef())
        
        # print(obj_KN + " Geometry: " + str(countGeom), end = ' ')
    
    def addMultiPoint(self, obj_KN, mp):
        with open(self.tempFile, 'a') as fp:
            res = [f'MULTIPOINT {mp.GetGeometryCount()}\n']
            for i in range(0, mp.GetGeometryCount()):
                res.append(f'{mp.GetGeometryRef(i).GetX()} {mp.GetGeometryRef(i).GetY()}\n')
            res.append("\tSymbol (35,0,12)\n")
            # for elem in res: print(elem)
            fp.writelines(res)
            fp.close()
        with open("temp.mid", 'a') as fp:
            fp.write("\"" + obj_KN + "\"")
            fp.close()
    
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
        elif geoType == ogr.wkbPoint:       geomMultiPoint.AddGeometry(geometry)
        
        elif geoType == ogr.wkbMultiPolygon:    addMultiGeometry(geometry, geomPolygon)
        elif geoType == ogr.wkbMultiLineString: addMultiGeometry(geometry, geomPolyline)
        elif geoType == ogr.wkbMultiPoint:      addMultiGeometry(geometry, geomMultiPoint)
        
        elif geoType == ogr.wkbGeometryCollection:
            for i in range(0, geometry.GetGeometryCount()):
                g = geometry.GetGeometryRef(i)
                gType = g.GetGeometryType()

                # print("Тип вложенной геометрии: " + g.GetGeometryName())

                if gType == ogr.wkbPolygon:         geomPolygon.AddGeometry(g)
                elif gType == ogr.wkbLineString:    geomPolyline.AddGeometry(g)
                elif gType == ogr.wkbPoint:         geomMultiPoint.AddGeometry(g)

                elif gType == ogr.wkbMultiPolygon:    addMultiGeometry(g, geomPolygon)
                elif gType == ogr.wkbMultiLineString: addMultiGeometry(g, geomPolyline)
                elif gType == ogr.wkbMultiPoint:      addMultiGeometry(g, geomMultiPoint)
                
                else: print(mifSrc + "No geometry")
        else: print(mifSrc + "No geometry")

        # print("Количество полигонов: " + str(geomPolygon.GetGeometryCount()))
        # print("Количество полилиний: " + str(geomPolyline.GetGeometryCount()))
        # print("Количество точек: " + str(geomMultiPoint.GetGeometryCount()))
    
    # print(geomPolygon.GetGeometryCount())
    # print(geomPolyline.GetGeometryCount())
    # print(geomMultiPoint.GetGeometryCount())

    # print(geomMultiPoint)
    
    if geomPolygon.GetGeometryCount():      geomcol.AddGeometry(geomPolygon)
    if geomPolyline.GetGeometryCount():     geomcol.AddGeometry(geomPolyline)
    # if geomMultiPoint.GetGeometryCount():   geomcol.AddGeometry(geomMultiPoint)
    
    # print(geomcol)
    # print("Add: " + feature.GetField("NOTE") + " Count: " + str(feature.GetGeometryRef().GetGeometryCount()))

    return (geomcol, geomMultiPoint)

if __name__ == '__main__':
    # Create result file
    resultFile = "result"

    # Processing source files
    folder = '86_02-15p1/'
    # folder = 'borders_geodata_86/'
    # mifSrc = "collection.mif"

    # filesList = os.listdir(folder)
    filesList = ['collection.mif']

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

    for mifSrc in filesList:
        # Processing each MIF file
        if mifSrc.endswith('.mif'):
            try:
                dataSource = ogr.Open(folder + mifSrc, 0)
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
                    # print('Total Lines:', count + 1)

                    # Add feature in result layer
                    if count:
                        mif.write("Collection " + str(count + 1))
                    mid.write("\"" + obj_KN + "\"\r")
                    writeMif(mif, "temp")

                    temp.delete()
                    
                else:
                    print(mifSrc + " - найдена сторонняя графика")
                    protocol.append(mifSrc + ";\"найдена сторонняя графика\"\n")
                    
                srcLayer.ResetReading()
            
            except Exception:
                print(traceback.format_exc())
                protocol.append(mifSrc + ":\n")
                protocol.append(traceback.format_exc())

    mif.close()
    mid.close()
    with open("protocol.csv", "w") as csv:
        csv.writelines(protocol)
        csv.close()