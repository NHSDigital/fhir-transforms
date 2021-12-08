# fhir-transforms

Maps and example resources for use in FHIR version transformation

## Overview

The [FHIR Mapping Language](http://www.hl7.org/fhir/mapping-language.html) (FML) is an informational standard providing a specification of an interpreted language that can transform from one version of a resource to another. 

## Community documentation

Additional information can be found at

* [Using the FHIR Mapping Language](https://confluence.hl7.org/display/FHIR/Using+the+FHIR+Mapping+Language)
* [FHIR Mapping Language - Tutorial](https://www.hl7.org/fhir/mapping-tutorial.html)
  * [Tutorial implementation](https://www.hl7.org/fhir/mapping-tutorial.html)

## Transform tools

The following are tools that have been used to test the example transforms in this repo.

### Server implementations

[Matchbox](https://github.com/ahdis/matchbox) - based on [HAPI-FHIR Starter Project](https://github.com/hapifhir/hapi-fhir-jpaserver-starter)

Has a working StructureMap/$convert and StructureMap/$transform operations

#### a. Load the StructureMap into the server

To load the StructureMap into the server using cURL

```shell
curl -X POST -H "Accept: application/fhir+json;fhirVersion=4.0" -H "Content-Type: text/fhir-mapping" --data-binary "@./extension.map" http://localhost:8080/matchbox/fhir/StructureMap/$convert
```

where

```shell
"@./extension.map"
```

is the FML

#### b. Perform the transform

To perform the transform using cURL

```shell
curl -X POST -H "Accept: application/fhir+json;fhirVersion=4.0" -H "Content-Type: application/fhir+json;fhirVersion=4.0" --data-binary "@./source.json" http://localhost:8080/matchbox/fhir/StructureMap/$transform?source=http://basic.example/resource
```

where

```shell
@./source.json
```

is the resource to transform, and the source parameter in the URL

```shell
http://basic.example/resource
```

need to match the name of the map in the FML, e.g.

```
map "http://basic.test/medication-request" = "basic-test-medication-request"
...
```

See [here](http://www.hl7.org/fhir/mapping-language.html#metadata) for definiton of the FML line above

## CLI implementations

[FHIR Validator](https://confluence.hl7.org/display/FHIR/Using+the+FHIR+Validator) - part of the [HAPI FHIR - HL7 FHIR Core Artifacts](https://github.com/hapifhir/org.hl7.fhir.core)

Download the latest pre-built [validator_cli](https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar)

### Simple conversion of an extension

The following usage of the validator_cli 

```shell
java -jar validator_cli.jar ./source.json -transform http://basic.test/medication-request -version 4.0.1 -ig ./fml.map -output output.json
```

will update the values of

```
MedicationRequest.extension.url
MedicationRequest.extension.valueCodeableConcept.coding.system
```

where the `./source.json` is (a contrieved, incomplete MedicationRequest resource with an extension), i.e.

```json
{
  "resourceType": "MedicationRequest",
  "extension": [
    {
      "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-CareConnect-GPC-PrescriptionType-1",
      "valueCodeableConcept": {
        "coding": [
          {
            "code": "acute",
            "display": "Acute",
            "system": "https://fhir.nhs.uk/STU3/CodeSystem/CareConnect-PrescriptionType-1"
          }
        ]
      }
    }
  ]
}
```

and `./fmp.map` contains is the FHIR Mapping Language for the conversion.  The updated values are hardcoded string literal, i.e. `UPDATED DEFINITION HERE` and `UPDATED CODESYSTEM HERE`

```
map "http://basic.test/medication-request" = "basic-test-medication-request"
uses "http://hl7.org/fhir/StructureDefinition/MedicationRequest" alias MedicationRequest as source
uses "http://hl7.org/fhir/StructureDefinition/MedicationRequest" alias MedicationRequest as target
uses "http://hl7.org/fhir/StructureDefinition/CodeableConcept" alias CodeableConcept as source
uses "http://hl7.org/fhir/StructureDefinition/CodeableConcept" alias CodeableConcept as target
uses "http://hl7.org/fhir/StructureDefinition/Coding" alias Coding as source
uses "http://hl7.org/fhir/StructureDefinition/Coding" alias Coding as target
group MedicationRequest(source src : MedicationRequest, target tgt : MedicationRequest)  {
    src.extension as ext where $this.url='https://fhir.nhs.uk/STU3/StructureDefinition/Extension-CareConnect-GPC-PrescriptionType-1'
        -> tgt.extension as tgtext, tgtext.url='UPDATED DEFINITION HERE' then {
        ext.value : CodeableConcept as vs -> tgtext.value = create('CodeableConcept') as vt then CodeableConceptPrescriptionType(vs, vt);
     };
   }
group CodeableConceptPrescriptionType(source src : CodeableConcept, target tgt : CodeableConcept) {
    // src.coding -> tgt.coding; the short form is only woking when you have a <<type>>
    src.coding -> tgt.coding;
    src.text as text -> tgt.text = text;
}
group Coding(source src : Coding, target tgt : Coding) <<type+>> {
    src.system as system where $this='https://fhir.nhs.uk/STU3/CodeSystem/CareConnect-PrescriptionType-1' -> tgt.system = 'UPDATED CODESYSTEM HERE';
    src.version as version -> tgt.version = version;
    src.code as code -> tgt.code = code;
    src.display as display -> tgt.display = display;
    src.userSelected as userSelected -> tgt.userSelected = userSelected;
}
```

the output procduced, i.e. `output.json` should be

```json
{
  "resourceType": "MedicationRequest",
  "extension": [
    {
      "url": "UPDATED DEFINITION HERE",
      "valueCodeableConcept": {
        "coding": [
          {
            "system": "UPDATED CODESYSTEM HERE",
            "code": "acute",
            "display": "Acute"
          }
        ]
      }
    }
  ]
}
```

## TODO

* Update README with a more complete example.
* Describe how to use the validator_cli to convert between based conversions without explicitly providing an FML map.
