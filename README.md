## MIV2DATEXII

:slightly_smiling_face: Live traffic-flow data of Flanders' highways is published as open data  
:worried: It is published in a custom XML format  
:tada: MIV2DATEXII

This library provides a Python API as well as a command line interface to convert MIV publications to the European DATEXII standard for publication of traffic related data.

#### Meten-in-Vlaanderen (MIV)

MIV is a dataset containing minutely updated information on traffic flow on Flemish roads. 
For more info:
- [opendata.vlaanderen.be](https://opendata.vlaanderen.be/dataset/7a4c24dc-d3db-460a-b73b-cf748ecb25dc)
- [verkeerscentrum.be](https://www.verkeerscentrum.be/data)
- [data.gov.be](https://data.gov.be/en/node/58556)

#### DATEXII
[The official DATEX2 website](https://datex2.eu/datex2/about)

### Requirements
- \>= Python 3.7
- pip3 ([installation instructions](https://pip.pypa.io/en/stable/installing))

### Installation
```
python3 -m pip install git+https://github.com/MikiDi/MIV2DATEXII.git
```

### Usage
Converting the locations table
```
curl http://miv.opendata.belfla.be/miv/configuratie/xml | miv2datex2 > miv_datex_locations.xml
```
Converting minutely data
```
curl http://miv.opendata.belfla.be/miv/verkeersdata | miv2datex2 > miv_datex_measurements.xml
```
### Useful resources:

- [DATEXII v2.3 browsable model](http://d2docs.ndwcloud.nu/_static/umlmodel/v2.3/index.htm)
- [Example DATEXII publications of the Netherlands](https://www.ndw.nu/documenten/nl/#cat_3)

### Feedback / Contributing

This library for sure isn't perfect. Suggestions, bug reports and pull requests are very welcome. :slightly_smiling_face: