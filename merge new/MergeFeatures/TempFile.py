from osgeo import ogr

class TempFile:
    tempName = "temp"
    tempMif = tempName + ".mif"
    tempMid = tempName + ".mid"

    def __init__(self, obj_KN, geoms):
        self.tempDriver = ogr.GetDriverByName("MapInfo File")
        tempSource = self.tempDriver.CreateDataSource(self.tempMif)
        self.tempLayer = tempSource.CreateLayer("temp")

        idField = ogr.FieldDefn("NOTE", ogr.OFTString)
        self.tempLayer.CreateField(idField)

        newFeature = ogr.Feature(self.tempLayer.GetLayerDefn())

        geomcol =  ogr.Geometry(ogr.wkbGeometryCollection)
        if geoms.geomPolygon.GetGeometryCount():      geomcol.AddGeometry(geoms.geomPolygon)
        if geoms.geomPolyline.GetGeometryCount():     geomcol.AddGeometry(geoms.geomPolyline)

        newFeature.SetGeometry(geomcol)
        newFeature.SetField("NOTE", obj_KN)
        self.tempLayer.CreateFeature(newFeature)
        
        countGeom = newFeature.GetGeometryRef().GetGeometryCount()

        if geoms.geomMultiPoint.GetGeometryCount():
            self.addMultiPoint(obj_KN, geoms.geomMultiPoint)
            countGeom += 1

        # print(newFeature.GetGeometryRef())
        
        # print(obj_KN + " Geometry: " + str(countGeom), end = ' ')
    
    def addMultiPoint(self, obj_KN, mp):
        with open(self.tempMif, 'a') as fp:
            res = [f'MULTIPOINT {mp.GetGeometryCount()}\n']
            for i in range(0, mp.GetGeometryCount()):
                res.append(f'{mp.GetGeometryRef(i).GetX()} {mp.GetGeometryRef(i).GetY()}\n')
            res.append("\tSymbol (35,0,12)\n")
            # for elem in res: print(elem)
            fp.writelines(res)
            fp.close()
        with open(self.tempMid, 'a') as fp:
            fp.write("\"" + obj_KN + "\"")
            fp.close()
    
    def getCount(self):
        # open file in read mode
        with open(self.tempMid, 'r') as fp:
            for count, line in enumerate(fp):
                pass
        return count + 1
        # print('Total Lines:', count + 1)

    def delete(self):
        self.tempDriver.DeleteDataSource(self.tempMif)