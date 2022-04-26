# Tutorial

## Community documentation

Additional information, the specification and more in depth tutorials can be found at

* [Using the FHIR Mapping Language](https://confluence.hl7.org/display/FHIR/Using+the+FHIR+Mapping+Language)
* [FHIR Mapping Language - Tutorial](https://www.hl7.org/fhir/mapping-tutorial.html)
  * [Tutorial implementation](https://github.com/ahdis/fhir-mapping-tutorial.git)

## Overview

The [resources](../) folder contains folder for different projects.  Each folder will contain seperate folders per resource.  Each resource folder will then contain a folder for input, for maps and a folder for expected out.  See the directory diagram in the [README](../../) at the root of the repo for further details.

This section will cover other tools, such as the [Matchbox](https://github.com/ahdis/matchbox) server that has a working %covert operation for converting FML to StructureMap's.

This section will describe carrying out transforms using the $covert and $transform operations in the [Matchbox](https://github.com/ahdis/matchbox) server.  It will also cover the following usuage of the validator_cli, which is want the pipeline in this repo uses.

```shell
java -jar validator_cli.jar <input source> -transform <Transform name> -version <FHIR version> -ig <FML or StructureMap defining transform> -output <output file>
```

A demo of using the validator_cli in the following way

```shell
java -jar validator_cli.jar <input source> -version <source FHIR version> -to-version <transformed FHIR version> -output <output file>
```

can be found at [hapi-fhir-3to4-demo](https://github.com/declankieran-nhsd/hapi-fhir-3to4-demo).  This mode uses StructureMap's that are downloaded to a local cache, i.e. the FML or StructureMap is not passed in with -ig.  The primary use of this would be to transform between base resources as opposed to custom extensions as is the case in this repo.

## Example transform to perform

The values of

```Haskell
MedicationRequest.extension.url
MedicationRequest.extension.valueCodeableConcept.coding.system
```

will be updated in the source

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

## Perform a transform using the Matchbox server

The [Matchbox](https://github.com/ahdis/matchbox) FHIR server is based on [HAPI-FHIR Starter Project](https://github.com/hapifhir/hapi-fhir-jpaserver-starter) has working StructureMap/$convert and StructureMap/$transform operations

The server has working StructureMap/$convert and StructureMap/$transform operations.  The FML must be first loaded into the server as a StructureMap.  The transform can then be performed.

### a. Run the Matchbox server

For details on how to build and run the docker image of the matchbox server, see the README [here](https://github.com/ahdis/matchbox)

### b. Load the StructureMap into the server 

To convert the FML to a StructureMap that can be posted to the server using cURL (assuming a local instance of the server listening on 8080)

```shell
curl -X POST -H "Accept: application/fhir+json;fhirVersion=4.0" -H "Content-Type: text/fhir-mapping" --data-binary "@./resourcename/maps/sourcename.map" http://localhost:8080/matchbox/fhir/StructureMap/$convert
```

where

```shell
"@./resourcename/maps/sourcename.map" 
```

is the FML.  The server will also return the StructureMap.

| TIP: When using the validator_cli.jar, the input to -ig switch can be FML or a StructureMap, but generating a StructureMap using the server can be useful in providing a level of analysis on the validity of the FML.|
| --- |

### c. Perform the transform

To perform the transform using cURL

```shell
curl -X POST -H "Accept: application/fhir+json;fhirVersion=4.0" -H "Content-Type: application/fhir+json;fhirVersion=4.0" --data-binary "@./resourcename/input/sourcename_001.json" http://localhost:8080/matchbox/fhir/StructureMap/\$transform?source=http://fhir.nhs.uk/StructureMap/sourcename
```

where

```shell
"@./resourcename/maps/sourcename_001.json" 
```

is the resource to transform, and the source parameter in the URL

```shell
http://fhir.nhs.uk/StructureMap/sourcename
```

needs to match the name of the map in the FML to indicate which transform to run, e.g.

```
map "http://fhir.nhs.uk/StructureMap/sourcename" = "Example map"
```

See [here](http://www.hl7.org/fhir/mapping-language.html#metadata) for the definition of the FML line above

## Perform a transform using the validator_cli

The pipeline in github actions uses this way of carrying out the transforms by downloading the latest pre-built [validator_cli.jar](https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar)

The [FHIR Validator](https://confluence.hl7.org/display/FHIR/Using+the+FHIR+Validator) is part of the [HAPI FHIR - HL7 FHIR Core Artifacts](https://github.com/hapifhir/org.hl7.fhir.core)

### Conversion using the FML (as opposed to StructureMap)

> **NOTE**: The StructureMap that is returned from the Matchbox server in [(b. Load the StructureMap into the server)](####b. Load the StructureMap into the server), can be directly used in place of the FML, e.g. structuremap.json instead of sourcename.map.

The following usage of the validator_cli 

```shell
java -jar validator_cli.jar ./resourcename/input/sourcename_001.json -transform http://fhir.nhs.uk/StructureMap/sourcename -version 4.0.1 -ig ./resourcename/maps/sourcename.map -output /tmp/output.json
```

will update the values of

```Haskell
MedicationRequest.extension.url
MedicationRequest.extension.valueCodeableConcept.coding.system
```

where the `./resourcename/input/sourcename_001.json` is a basic example of a PrescriptionType-1 extension,

#### Input

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

and `./resourcename/maps/sourcename.map` contains the FHIR Mapping Language for the conversion.  The updated values are hardcoded string literals, i.e. `UPDATED DEFINITION HERE` and `UPDATED CODESYSTEM HERE`

#### FML Map

```Haskell
map "http://fhir.nhs.uk/StructureMap/sourcename" = "Example map"
uses "http://hl7.org/fhir/StructureDefinition/MedicationRequest" alias MedicationRequest as source
uses "http://hl7.org/fhir/StructureDefinition/MedicationRequest" alias MedicationRequest as target
uses "http://hl7.org/fhir/StructureDefinition/Coding" alias Coding as source
uses "http://hl7.org/fhir/StructureDefinition/Coding" alias Coding as target

group MedicationRequest(source src : MedicationRequest, target tgt : MedicationRequest)  {
    src.extension as ext where $this.url='https://fhir.nhs.uk/STU3/StructureDefinition/Extension-CareConnect-GPC-PrescriptionType-1'
        -> tgt.extension as tgtext, tgtext.url='UPDATED DEFINITION HERE' then {
        ext.value : CodeableConcept as vs -> tgtext.value = create('CodeableConcept') as vt then CodeableConceptPrescriptionType(vs, vt);
    };
}

group CodeableConceptPrescriptionType(source src, target tgt) {
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

the output produced, i.e. `/tmp/output.json` should be

#### Output

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
