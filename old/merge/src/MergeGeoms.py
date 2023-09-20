from osgeo import ogr

class MergeGeoms:
    geomPolygon = ogr.Geometry(ogr.wkbMultiPolygon)
    geomPolyline = ogr.Geometry(ogr.wkbMultiLineString)
    geomMultiPoint = ogr.Geometry(ogr.wkbMultiPoint)

    def __init__(self, srcLayer):
        self.srcLayer = srcLayer

        for feature in srcLayer:
            geometry = feature.GetGeometryRef()
            geoType = geometry.GetGeometryType()

            # print("\nТип геометрии: " + geometry.GetGeometryName())
            
            if geoType == ogr.wkbGeometryCollection:
                for i in range(0, geometry.GetGeometryCount()):
                    g = geometry.GetGeometryRef(i)
                    gType = g.GetGeometryType()

                    # print("\tТип вложенной геометрии: " + g.GetGeometryName())

                    self.addGeom(g, gType)
            else: self.addGeom(geometry, geoType)

            # print("Количество полигонов: " + str(self.geomPolygon.GetGeometryCount()))
            # print("Количество полилиний: " + str(self.geomPolyline.GetGeometryCount()))
            # print("Количество точек: " + str(self.geomMultiPoint.GetGeometryCount()))
        
        # print("Всего полигонов: " + str(self.geomPolygon.GetGeometryCount()))
        # print("Всего полилиний: " + str(self.geomPolyline.GetGeometryCount()))
        # print("Всего точек: " + str(self.geomMultiPoint.GetGeometryCount()))

        # print(geomMultiPoint)

        # print("Add: " + feature.GetField("NOTE") + " Count: " + str(feature.GetGeometryRef().GetGeometryCount()))
    
    def addGeom(self, geometry, geoType):
        if geoType == ogr.wkbPolygon:       self.geomPolygon.AddGeometry(geometry)
        elif geoType == ogr.wkbLineString:  self.geomPolyline.AddGeometry(geometry)
        elif geoType == ogr.wkbPoint:       self.geomMultiPoint.AddGeometry(geometry)
        
        elif geoType == ogr.wkbMultiPolygon:    self.addMultiGeometry(geometry, self.geomPolygon)
        elif geoType == ogr.wkbMultiLineString: self.addMultiGeometry(geometry, self.geomPolyline)
        elif geoType == ogr.wkbMultiPoint:      self.addMultiGeometry(geometry, self.geomMultiPoint)

        else: print(self.srcLayer.GetName() + " No geometry")
    
    @staticmethod
    def addMultiGeometry(srcGeom, outGeom):
        for i in range(0, srcGeom.GetGeometryCount()):
            outGeom.AddGeometry(srcGeom.GetGeometryRef(i))
        # print("Стало " + outGeom.GetGeometryName() + ": " + str(outGeom.GetGeometryCount()))