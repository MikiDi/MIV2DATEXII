#!/usr/bin/python3
import xml.etree.ElementTree as ET

from datetime import datetime

from .lib.pythonize_iso_timestamp import pythonize_iso_timestamp

class MeasurementPublication():
    """docstring for MeetpuntenConfig."""
    def __init__(self, tijd=datetime.now()):
        super(MeasurementPublication, self).__init__()
        self.time_publication = tijd
        self.time_last_config_change = None
        self.measurements = []

    @property
    def measurement_time_default(self):
        return self.measurements[0].measurement_time

    def __iter__(self):
        return iter(self.measurements)

    @classmethod
    def fromXmlString(cls, string):
        root = ET.fromstring(string)

        pubtime = datetime.fromisoformat(pythonize_iso_timestamp(root.find('tijd_publicatie').text))
        measurementpub = cls(pubtime)
        measurementpub.time_last_config_change = datetime.fromisoformat(pythonize_iso_timestamp(root.find('tijd_laatste_config_wijziging').text))
        for meetpunt in root.iter('meetpunt'):
            mp = Measurement.fromXml(meetpunt)
            measurementpub.measurements.append(mp)

        return measurementpub

    def byId(self):
        """Returns a dict of {unieke_id: mp1_object, unieke_id2: mp2_object, ...}"""
        return {mp.unique_id: mp for mp in self.measurements}

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
            'xsi:type': 'MeasuredDataPublication',
            'lang': 'nl'
        })
        # lang = ET.SubElement(pub, 'defaultLanguage')
        # lang.text = 'nl'
        pubt = ET.SubElement(pub, 'publicationTime')
        pubt.text = self.time_publication.isoformat()

        sup_id = ET.SubElement(pub, 'publicationCreator')
        country = ET.SubElement(sup_id, 'country')
        country.text = 'be'
        nid = ET.SubElement(sup_id, 'nationalIdentifier')
        nid.text = 'required'

        ET.SubElement(pub, 'measurementSiteTableReference', {
            'id': 'config',
            'version': str(int(self.time_last_config_change.timestamp())),
            'targetClass': 'MeasurementSiteTable'
        })

        hi = ET.SubElement(pub, 'headerInformation')
        conf = ET.SubElement(hi, 'confidentiality')
        conf.text = 'noRestriction'
        instat = ET.SubElement(hi, 'informationStatus')
        instat.text = 'technicalExercise' # 'real'

        for mp in self:
            pub.append(mp.toDatexXml())
        return d2lm

class Measurement(object):
    """docstring for Meetpunt."""
    def __init__(self, unieke_id):
        super(Measurement, self).__init__()
        self.site_id = unieke_id
        self.measurement_time = None
        self.last_modified_time = None
        self.measurement_period = 60
        self.valid = True
        self.defect = False
        self.available = True
        self.occupancy_rate = 0
        self.measurements_by_category = {}

    def __str__(self):
        return """
        Meting {0}:
        """.format(self.site_id)

    @classmethod
    def fromXml(cls, mp_xml):
        mp = cls(int(mp_xml.get('unieke_id')))
        mp.lve_nr = int(mp_xml.find('lve_nr').text)
        mp.measurement_time = datetime.fromisoformat(pythonize_iso_timestamp(mp_xml.find('tijd_waarneming').text))
        mp.last_modified_time = datetime.fromisoformat(pythonize_iso_timestamp(mp_xml.find('tijd_laatst_gewijzigd').text))
        mp.valid = mp_xml.find('geldig').text == '0'
        mp.available = mp_xml.find('beschikbaar').text == '1'
        mp.defect = mp_xml.find('defect').text == '0'
        mp.occupancy_rate = int(mp_xml.find('rekendata/bezettingsgraad').text) # in times 10ms in a minute

        for md in mp_xml.iter('meetdata'):
            mp.measurements_by_category[int(md.get('klasse_id'))] = {
                'verkeersintensiteit': int(md.find('verkeersintensiteit').text),
                'voertuigsnelheid_rekenkundig': int(md.find('voertuigsnelheid_rekenkundig').text),
                'voertuigsnelheid_harmonisch': int(md.find('voertuigsnelheid_harmonisch').text)
            }
        return mp

    def toDatexXml(self):
        sm = ET.Element('siteMeasurements')

        ET.SubElement(sm, 'measurementSiteReference', {
            'id': 'id to table',
            'version': '1',
            'targetClass': 'MeasurementSiteRecord'
        })
        mtd = ET.SubElement(sm, 'measurementTimeDefault')
        mtd.text = self.measurement_time.isoformat()

        measurements_per_category = 2
        for index, props in self.measurements_by_category.items():
            calc_index = index*measurements_per_category-1
            mv = ET.Element('measuredValue', {'index': str(calc_index)})
            mv2 = ET.SubElement(mv, 'measuredValue')
            bd = ET.SubElement(mv2, 'basicData', {'xsi:type': 'TrafficFlow'})
            vf = ET.SubElement(bd, 'vehicleFlow')
            vfr = ET.SubElement(vf, 'vehicleFlowRate')
            vfr.text = str(int(props['verkeersintensiteit']/self.measurement_period*60*60))
            sm.append(mv)

            calc_index = index*measurements_per_category
            mv = ET.Element('measuredValue', {'index': str(calc_index)})
            mv2 = ET.SubElement(mv, 'measuredValue')
            bd = ET.SubElement(mv2, 'basicData', {'xsi:type': 'TrafficSpeed'})
            vf = ET.SubElement(bd, 'averageVehicleSpeed')
            vfr = ET.SubElement(vf, 'speed')
            vfr.text = str(props['voertuigsnelheid_rekenkundig'])
            sm.append(mv)

        calc_index = len(self.measurements_by_category.keys())*2+1
        mv = ET.Element('measuredValue', {'index': str(calc_index)})
        mv2 = ET.SubElement(mv, 'measuredValue')
        bd = ET.SubElement(mv2, 'basicData', {'xsi:type': 'TrafficConcentration'})
        vf = ET.SubElement(bd, 'occupancy')
        vfr = ET.SubElement(vf, 'percentage')
        vfr.text = str(self.occupancy_rate*100/60)
        sm.append(mv)

        return sm
