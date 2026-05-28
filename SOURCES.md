# Sources Document

## Data Source Format Research

### SAP Data Formats

**IDoc (Intermediate Document) Format:**
- IDocs are SAP's standard format for asynchronous data exchange
- Structure: Control Record (EDI_DC40) + Data Records (segments) + Status Records
- Relevant message types: MATMAS (material master), MBGMCR (goods movement)
- Fields: Material number (MATNR), Quantity (MENGE), Unit (MEINS), Cost Center (KOSTL), Transaction Date (BUDAT)

**Sample IDoc XML:**
```xml
<IDOC BEGIN="1">
  <EDI_DC40 SEGMENT="1">
    <MESTYP>MATMAS</MESTYP>
    <SNDPRN>SAPCLNT100</SNDPRN>
  </EDI_DC40>
  <E1MARAM SEGMENT="1">
    <MATNR>DIESEL-001</MATNR>
    <MENGE>1500.000</MENGE>
    <MEINS>GAL</MEINS>
    <KOSTL>CC-FLEET</KOSTL>
    <BUDAT>20240315</BUDAT>
    <WERKS>PLANT-01</WERKS>
  </E1MARAM>
</IDOC>
```

**SAP CSV Export:**
```csv
Material,Quantity,Unit,Cost Center,Date,Plant,Description
DIESEL-001,1500,GAL,CC-FLEET,2024-03-15,PLANT-01,Fleet diesel fuel
NATGAS-002,5000,THERMS,CC-FACILITY,2024-03-15,PLANT-01,Natural gas heating
```

**References:**
- SAP IDoc Documentation: help.sap.com/docs/SAP_NETWEAVER
- SAP Material Master: help.sap.com/docs/SAP_S4HANA

---

### Green Button Standard (Utility Data)

**Format:** Atom Syndication Format with ESPI (Energy Services Provider Interface) extensions
**Standard:** NAESB REQ.21 Energy Services Provider Interface
**Key Elements:**
- `<UsagePoint>`: Metering location identifier
- `<MeterReading>`: Collection of interval data
- `<IntervalBlock>`: Time-series usage data with start/duration
- `<IntervalReading>`: Individual measurement with value
- `<ReadingType>`: Unit of measure, power of ten multiplier

**Sample Green Button XML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:espi="http://naesb.org/espi">
  <entry>
    <content>
      <espi:UsagePoint>
        <espi:ServiceCategory>
          <espi:kind>0</espi:kind>
        </espi:ServiceCategory>
      </espi:UsagePoint>
    </content>
  </entry>
  <entry>
    <content>
      <espi:MeterReading>
        <espi:IntervalBlock>
          <espi:interval>
            <espi:start>1710460800</espi:start>
            <espi:duration>3600</espi:duration>
          </espi:interval>
          <espi:IntervalReading>
            <espi:value>1250</espi:value>
          </espi:IntervalReading>
        </espi:IntervalBlock>
      </espi:MeterReading>
    </content>
  </entry>
</feed>
```

**References:**
- Green Button Alliance: greenbuttonalliance.org
- NAESB ESPI Standard: naesb.org
- Green Button Developer Resources: greenbuttondata.org

---

### SAP Concur Travel Data

**Format:** JSON via REST API
**API Version:** Concur Travel API v4
**Key Data:**
- Trip records with itinerary segments
- Each segment: transportation mode, origin/destination, distance, class of service
- Carbon emissions calculations (ISO 14083)

**Sample Concur JSON:**
```json
{
  "TripId": "TRIP-2024-001",
  "TripName": "Client Meeting NYC",
  "Segments": [
    {
      "SegmentType": "AIR",
      "ClassOfService": "Economy",
      "StartLocation": "SFO",
      "EndLocation": "JFK",
      "StartDate": "2024-03-20",
      "EndDate": "2024-03-20",
      "Distance": 2586,
      "DistanceUnit": "miles",
      "Carrier": "United Airlines",
      "CarbonEmissions": 0.456,
      "EmissionsUnit": "tonnes_co2e"
    },
    {
      "SegmentType": "HOTEL",
      "StartLocation": "New York, NY",
      "StartDate": "2024-03-20",
      "EndDate": "2024-03-22",
      "CarbonEmissions": 0.089,
      "EmissionsUnit": "tonnes_co2e"
    }
  ]
}
```

**References:**
- SAP Concur Developer Center: developer.concur.com
- Concur Travel API: developer.concur.com/api-reference/travel
- ISO 14083: Greenhouse gas emissions from transport

---

## Ingestion Mechanism Justification

| Source | Format | Mechanism | Rationale |
|--------|--------|-----------|-----------|
| SAP | IDoc XML | File upload (POST) | IDocs are typically exported as files; real-time integration requires SAP middleware |
| SAP | CSV | File upload (POST) | CSV exports are the simplest integration path for organizations without middleware |
| Green Button | Atom XML | File upload (POST) | DMD (Download My Data) provides XML files; CMD requires OAuth2 with each utility |
| Concur | JSON | API POST | Concur provides REST APIs; data can be fetched and forwarded to our ingestion endpoint |
