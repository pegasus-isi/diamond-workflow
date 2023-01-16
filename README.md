# Diamond Workflow 

# Dependencies
- Pegasus v5.0+
- Python 3.6+

![diamond-workflow](https://user-images.githubusercontent.com/36110304/212752545-1859e0b2-54a4-45d1-9164-f2fa6265a36a.png)

# File Description

<b>plan.sh:</b> Consists of all commands to be executed to run the workflow. Takes care of planning the pegasus workflow and initialising where the input files are and where output files should be located after execution of workflow. 

<b>workflow_generator.py:</b> Creates the abstract workflow, the replica catalog, the transformation catalog, and the site catalog. There are three jobs: findrange, preprocess analyse. These are used to invoke the executables which are present in bin folder.

<b>bin Folder:</b> Contains the executable scripts: findrange, preprocess, analyze

<b>Input Folder:</b> Contains all the input files to be used in the workflow.

# How to run the workflow?
```
# Plan and run the workflow generator to create an abstract workflow for the given input files
./workflow_generator.py   # Generate the workflow.yaml file
./plan.sh workflow.yaml
```
