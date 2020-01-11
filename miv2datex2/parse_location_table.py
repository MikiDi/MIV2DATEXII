#!/usr/bin/python3
import xml.etree.ElementTree as ET

from datetime import datetime

class LocationTable():
    """docstring for LocationTable."""
    def __init__(self, tijd=datetime.now(), meetpunten=[]):#TODO datetime
        super(LocationTable, self).__init__()
        self.tijd_laatste_config_wijziging = tijd
        self.meetpunten = meetpunten

    def __iter__(self):
        return iter(self.meetpunten)

    @classmethod
    def fromXmlString(cls, string):
        root = ET.fromstring(string)

        meetpunten = []
        try:
            time = datetime.fromisoformat(root.find('tijd_laatste_config_wijziging').text)
        except AttributeError: #datetime.datetime.fromisoformat only >= Python 3.7
            time = datetime.now()
        for meetpunt in root.iter('meetpunt'):
            mp = Meetpunt.fromXml(meetpunt)
            meetpunten.append(mp)

        return cls(time, meetpunten) #TODO datetime

    def groupByLve(self):
        """Returns a dict of {lve_id: [mp1, mp2, ...], lve_id2: ...}"""
        meetpunten = {}
        for mp in self.meetpunten:
            lve = mp.lve_nr
            meetpunten.setdefault(lve, []).append(mp) #add key or create dict and add key
        return meetpunten

    def groupByBeschrijvende_id(self):
        meetpunten = {}
        for mp in self.meetpunten:
            a, b, c, d = mp.beschrijvende_id[0], mp.beschrijvende_id[1:4], mp.beschrijvende_id[4], mp.beschrijvende_id[5:7]
            meetpunten.setdefault(b, []).append((a, c, d, mp)) #add key or create dict and add key
        return meetpunten

    def byId(self):
        """Returns a dict of {unieke_id: mp1_object, unieke_id2: mp2_object, ...}"""
        return {mp.unieke_id: mp for mp in self.meetpunten}

    def toDatexXml(self):
        d2lm = ET.Element('d2LogicalModel', {
            'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns': 'http://datex2.eu/schema/2/2_0',
            'modelBaseVersion': '2',
            'xsi:schemaLocation': 'http://datex2.eu/schema/2/2_0 http://datex2.eu/schema/2/2_3/DATEXIISchema_2_2_3.xsd'
        })
        ex = ET.SubElement(d2lm, 'exchange')
        sup_id = ET.SubElement(ex, 'supplierIdentification')
        country = ET.SubElement(sup_id, 'country')
        country.text = 'be'
        nid = ET.SubElement(sup_id, 'nationalIdentifier')
        nid.text = 'required'

        pub = ET.SubElement(d2lm, 'payloadPublication', {
            'xsi:type': 'MeasurementSiteTablePublication',
            'lang': 'nl'
        })
        # lang = ET.SubElement(pub, 'defaultLanguage')
        # lang.text = 'nl'
        pubt = ET.SubElement(pub, 'publicationTime')
        pubt.text = self.tijd_laatste_config_wijziging.isoformat()

        sup_id = ET.SubElement(pub, 'publicationCreator')
        country = ET.SubElement(sup_id, 'country')
        country.text = 'be'
        nid = ET.SubElement(sup_id, 'nationalIdentifier')
        nid.text = 'required'

        hi = ET.SubElement(pub, 'headerInformation')
        conf = ET.SubElement(hi, 'confidentiality')
        conf.text = 'noRestriction'
        instat = ET.SubElement(hi, 'informationStatus')
        instat.text = 'technicalExercise' # 'real'

        mst = ET.SubElement(pub, 'measurementSiteTable', {
            'id': 'config',
            'version': str(int(self.tijd_laatste_config_wijziging.timestamp()))
        })

        for mp in self:
            mst.append(mp.toDatexXml())

        return d2lm

class Meetpunt():
    """docstring for Meetpunt."""
    def __init__(self, unieke_id):
        super(Meetpunt, self).__init__()
        self.unieke_id = unieke_id

    @property
    def datex_lane_type(self):
        if self.rijstrook.startswith('R'):
            lane_nr = int(self.rijstrook[1:])
            if lane_nr >= 10:
                return 'lane' + str(lane_nr-9)
            else:
                return None
        elif self.rijstrook.startswith('P'):
            return 'emergencyLane'
        elif self.rijstrook == 'R':
            return 'hardShoulder'
        elif self.rijstrook == 'B':
            return 'busLane'
        elif self.rijstrook == 'S':
            return 'rushHourLane'
        return None

    @property
    def datex_direction(self):
        if self.rijstrook.startswith('TR'):
            return 'opposite'
        else:
            return None

    def __str__(self):
        return """
        Meetpunt {0}:
        beschrijvende_id: {1}
        volledige_naam: {2}
        Ident_8: {3}
        lve_nr: {4}
        Kmp_Rsys: {5}
        Rijstrook: {6}
        lengtegraad_EPSG_4326: {7}
        breedtegraad_EPSG_4326: {8}
        """.format(self.unieke_id,
                   self.beschrijvende_id,
                   self.volledige_naam,
                   self.ident_8,
                   self.lve_nr,
                   self.kmp_Rsys,
                   self.rijstrook,
                   self.lengtegraad_EPSG_4326,
                   self.breedtegraad_EPSG_4326)

    @classmethod
    def fromXml(cls, mp_xml):
        mp = cls(int(mp_xml.get('unieke_id')))
        mp.beschrijvende_id = mp_xml.find('beschrijvende_id').text
        mp.volledige_naam = mp_xml.find('volledige_naam').text
        mp.ident_8 = mp_xml.find('Ident_8').text
        mp.lve_nr = int(mp_xml.find('lve_nr').text)
        try:
            mp.kmp_Rsys = float(mp_xml.find('Kmp_Rsys').text.replace(',', '.'))
        except (ValueError, AttributeError):
            mp.kmp_Rsys = None
        mp.rijstrook = mp_xml.find('Rijstrook').text
        mp.lengtegraad_EPSG_4326 = float(mp_xml.find('lengtegraad_EPSG_4326').text.replace(',', '.'))
        mp.breedtegraad_EPSG_4326 = float(mp_xml.find('breedtegraad_EPSG_4326').text.replace(',', '.'))
        return mp

    def toDatexXml(self, versiontime=datetime.now()):
        """ versiontime is a datetime.datetime object """
        msr = ET.Element('measurementSiteRecord')
        msr.set('id', str(self.unieke_id))
        msr.set('version', '1')

        # msrrvt = ET.SubElement(msr, 'measurementSiteRecordVersionTime')
        # msrrvt.text = versiontime.isoformat()

        # cm = ET.SubElement(msr, 'computationMethod')

        mer = ET.SubElement(msr, 'measurementEquipmentReference')
        mer.text = str(self.lve_nr)

        # metu = ET.SubElement(msr, 'measurementEquipmentTypeUsed')
        # metu_val = ET.SubElement(ET.SubElement(metu, 'values'), 'value')
        # metu_val.set('lang', 'en')
        # metu_val.text = 'loop'

        msn = ET.SubElement(msr, 'measurementSiteName')
        msn_val = ET.SubElement(ET.SubElement(msn, 'values'), 'value')
        msn_val.set('lang', 'nl') # default
        msn_val.text = self.volledige_naam

        msnol = ET.SubElement(msr, 'measurementSiteNumberOfLanes')
        msnol.text = '1'

        msi = ET.SubElement(msr, 'measurementSiteIdentification')
        msi.text = self.beschrijvende_id

        LENGTH_CHARACTERISTICS_BY_CATEGORY = {
            1: (('greaterThan', 0), ('lessThan', 1.00)),
            2: (('greaterThan', 1.00), ('lessThan', 4.90)),
            3: (('greaterThan', 4.90), ('lessThan', 6.90)),
            4: (('greaterThan', 6.90), ('lessThan', 12.00)),
            5: (('greaterThan', 12.00),)
        }
        VALUE_TYPES = ('trafficFlow', 'trafficSpeed')

        for category, length_characteristics in LENGTH_CHARACTERISTICS_BY_CATEGORY.items():
            i = 0
            for value_type in VALUE_TYPES:
                i += 1
                calc_index = (len(VALUE_TYPES)*(category-1)) + i
                msc = ET.SubElement(msr, 'measurementSpecificCharacteristics', {'index': str(calc_index)})
                msc = ET.SubElement(msc, 'measurementSpecificCharacteristics')
                ET.SubElement(msc, 'period').text = '60.0'
                ET.SubElement(msc, 'specificLane').text = self.datex_lane_type
                ET.SubElement(msc, 'specificMeasurementValueType').text = value_type

                svc = ET.SubElement(msc, 'specificVehicleCharacteristics')
                for comparison_op, length in length_characteristics:
                    lc = ET.SubElement(svc, 'lengthCharacteristic')
                    ET.SubElement(lc, 'comparisonOperator').text = comparison_op
                    ET.SubElement(lc, 'vehicleLength').text = str(length)

        msc = ET.SubElement(msr, 'measurementSpecificCharacteristics', {'index': str(calc_index+1)})
        msc = ET.SubElement(msc, 'measurementSpecificCharacteristics')
        ET.SubElement(msc, 'period').text = '60.0'
        ET.SubElement(msc, 'specificLane').text = self.datex_lane_type
        ET.SubElement(msc, 'specificMeasurementValueType').text = 'trafficConcentration'
        svc = ET.SubElement(msc, 'specificVehicleCharacteristics')

        msl = ET.SubElement(msr, 'measurementSiteLocation')
        msl.set('xsi:type', 'Point')
        pc = ET.SubElement(ET.SubElement(msl, 'pointByCoordinates'), 'pointCoordinates')
        lat = ET.SubElement(pc, 'latitude') # Should be in ETRS89, but using WGS84 interchangeably shouldn't introduce errors > +/-1m
        lat.text = str(self.breedtegraad_EPSG_4326)
        lon = ET.SubElement(pc, 'longitude')
        lon.text = str(self.lengtegraad_EPSG_4326)

        # cm = ET.SubElement(msr, 'computationMethod')

        return msr
