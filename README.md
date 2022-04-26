# fhir-transforms

Maps and example resources for use in FHIR version transformation

## Overview

The [FHIR Mapping Language](http://www.hl7.org/fhir/mapping-language.html) (FML) is an informational standard providing a specification of an interpreted language that can transform from one version of a resource to another. 

## Content of this repository

This repository will provide maps and example inputs and output to be used in the transformation of UK NHS FHIR extensions using FML.

### Directory structure

![Directory structure](docs/scripts/rendered-diagrams/dia-directory-structure.svg?raw=true "Overview of directory structure with naming conventions.")

The following sections describe the structure and naming conventions used for the maps and inputs.

-------------------------

### A) ./resources folder

The top level of this folder will contain multiple folders named using general project names, following the convention of `<profile>-to-<profile>`.

e.g. 

[./resources/careconnect-to-ukcore](./resources/careconnect-to-ukcore)

> **NOTE**: The tutorial folder is an exception to this rule.

Within this folder, there will be multiple folders which will be named using FHIR resource names

e.g. 

[./resources/careconnect-to-ukcore/medicationrequest](./resources/careconnect-to-ukcore/medicationrequest)

At the next layer the folders here will be called

[/input](./resources/careconnect-to-ukcore/medicationrequest/input), [/expected](./resources/careconnect-to-ukcore/medicationrequest/expected), [/maps](./resources/careconnect-to-ukcore/medicationrequest/maps)

#### /input folder

This folder will contain examples to transform using a map.  The naming of this file MUST follow this convention

`<Type name>-<Type>-<[Version number]to[Version number]>_<Padded sequential number>.<json | xml>`

e.g. *MedicationStatusReason-Extension-3to4_000.json*

> **NOTE**: The tests use the names to match input with map, and transformed output with the expected output.

#### /expected folder

This folder will contain the expected output of a transform.  When the workflow pipeline performs a transformation, it will compare it with the corresponding expected file.  The naming convention that MUST be followed is the same as the input, i.e.

`<Type name>-<Type>-<[Version number]to[Version number]>_<Padded sequential number>.<json | xml>`

e.g. *MedicationStatusReason-Extension-3to4_000.json*

#### /maps folder

This folder will contain the maps for the transformation.  The file name convention for this is

`<Base input file name>.map`

where 

`<Base input file name>` = `<Type name>-<Type>-<[Version number]to[Version number]>`

i.e. the input file name without the padded number

e.g. *MedicationStatusReason-Extension-3to4.map*

By following these naming conventions, it will simplify the code of the tests for picking up and processing the files, and also make it clear from the output what has been processed in terms of success or failure.

-------------------------

### B) ./tests

The tope level of this folder will contain tests written using pytest.  A lib folder has been added for common functions.  The naming convention to follow here is

`test-<test name>.py`

and the tests should be implemented using pytest.

The [./tests/requirements.txt](./tests/requirements.txt) is to handle the python dependencies in the workflow pipeline.

#### 1. Transform tests

The test in ([./tests/test-resource-transforms.py](./tests/test-resource-transforms.py)) will do the following

* Scan all folders in [./resources](./resources) for input files  
* pytest will parameterise these and perform transforms on each
	* The map name is derived from the input file name
	* Each input file is transformed using the corresponding map
	* The creation of this file is asserted <sup>**(1)**</sup>
* The transform output is stored in /tmp
* The transform and expected are asserted to be equal <sup>**(2)**</sup>  
 
<sup>**(1)**</sup> The validator_cli seems to have non zero exits in some of its threads, so asserting on return code when using subprocess wasn't reliable.  Also testing the contents of stderr also didn't given consistent results.  The output file however is only ever created on success.  
<sup>**(2)**</sup> The json of the expected and the transform output is sorted by key and tested for equality.

#### 2. Validation tests

> **TODO**: Currently this has only be eyeballed in terms of expected data.  A script to test that all data that should been carried over was carried, and indicate any that was lost would be a useful check.  At that point it might make sense to indicate different types of failure, i.e. expected and unexpected.

-------------------------
	
### C) ./.github/workflows folder

Using github actions, it will be possible to drop in new input and output examples that can be automically checked on a push or PR using the latest version of the [validator_cli](https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar) (as mentioned in the previous section).

This will be useful for updating/refactoring maps's, but also for ensuring that the latest version of the validator_cli.jar is used to validate the maps.

#### 1. Validate tranforms

The workflow defined in [.github/workflows/validate-transforms.yml](.github/workflows/validate-transforms.yml) will do the following

* Download the validator_cli.jar from [here](https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar)
* Set up java to run the validator_cli.
* Set up python to run the test script
* Run the tests

## Tutorial

A simple tutorial along with details of community documentation can be found [here](./resources/tutorial)
