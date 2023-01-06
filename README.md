# Diamond Workflow 

# Dependencies
- Pegasus v5.0+
- HTCondor v10.2+
- Python 3.6+

![Diamond](https://user-images.githubusercontent.com/36110304/207698312-1c8724d5-7279-403a-81cf-41ea87309f5b.png)

# File Description

<b>plan.sh:</b> Consists of all commands to be executed to run the workflow. Takes care of planning the pegasus workflow and initialising where the input files are and where output files should be located after execution of workflow. 

<b>workflow_generator.py:</b> Creates the abstract workflow, the replica catalog, the transformation catalog, and the site catalog. It has three jobs: findrange, preprocess, analyze which are used to create the workflow. 

<b>bin Folder:</b> Contains the jobs: findrange, preprocess, analyze

<b>Input Folder:</b> Contains all the input files to be used in the workflow.

# How to run the workflow?
```
# Plan and run the workflow generator to create an abstract workflow for the given input files
./plan.sh
```
