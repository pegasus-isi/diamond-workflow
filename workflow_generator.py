#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path
from argparse import ArgumentParser

logging.basicConfig(level=logging.DEBUG)

# --- Import Pegasus API -----------------------------------------------------------
from Pegasus.api import *

class DiamondWorkflow():
    wf = None
    sc = None
    tc = None
    rc = None
    props = None

    dagfile = None
    wf_name = None
    wf_dir = None
    
    # --- Init ---------------------------------------------------------------------
    def __init__(self, dagfile="workflow.yml"):
        self.dagfile = dagfile
        self.wf_name = "diamond"
        self.wf_dir = Path(__file__).parent.resolve()

    
    # --- Write files in directory -------------------------------------------------
    def write(self):
        if not self.sc is None:
            self.sc.write()
        self.props.write()
        self.rc.write()
        self.tc.write()
        self.wf.write()


    # --- Configuration (Pegasus Properties) ---------------------------------------
    def create_pegasus_properties(self):
        self.props = Properties()

        # props["pegasus.monitord.encoding"] = "json"                                                                    
        #self.properties["pegasus.integrity.checking"] = "none"
        return


    # --- Site Catalog -------------------------------------------------------------
    def create_sites_catalog(self, exec_site_name="condorpool"):
        self.sc = SiteCatalog()

        shared_scratch_dir = os.path.join(self.wf_dir, "scratch")
        local_storage_dir = os.path.join(self.wf_dir, "output")

        local = Site("local")\
                    .add_directories(
                        Directory(Directory.SHARED_SCRATCH, shared_scratch_dir)
                            .add_file_servers(FileServer("file://" + shared_scratch_dir, Operation.ALL)),
                        
                        Directory(Directory.LOCAL_STORAGE, local_storage_dir)
                            .add_file_servers(FileServer("file://" + local_storage_dir, Operation.ALL))
                    )

        exec_site = Site(exec_site_name)\
                        .add_pegasus_profile(style="condor")\
                        .add_condor_profile(universe="vanilla")\
                        .add_profiles(Namespace.PEGASUS, key="data.configuration", value="condorio")

        self.sc.add_sites(local, exec_site)


    # --- Transformation Catalog (Executables and Containers) ----------------------
    def create_transformation_catalog(self, exec_site_name="condorpool"):
        self.tc = TransformationCatalog()

        # Add the preprocess executable
        preprocess = Transformation("preprocess", site=exec_site_name, pfn=os.path.join(self.wf_dir, "bin/preprocess"), is_stageable=True)
        # Add the findrange executable
        findrange = Transformation("findrange", site=exec_site_name, pfn=os.path.join(self.wf_dir, "bin/findrange"), is_stageable=True)
        # Add the analyze executable
        analyze = Transformation("analyze", site=exec_site_name, pfn=os.path.join(self.wf_dir, "bin/analyze"), is_stageable=True)
        
        self.tc.add_transformations(preprocess, findrange, analyze)


    # --- Replica Catalog ----------------------------------------------------------
    def create_replica_catalog(self):
        self.rc = ReplicaCatalog()

        # Add f.a replica
        self.rc.add_replica("local", "f.a", os.path.join(self.wf_dir, "input", "f.a"))

    
    # --- Create Workflow ----------------------------------------------------------
    def create_workflow(self):
        self.wf = Workflow(self.wf_name, infer_dependencies=True)
        
        # Add a preprocess job
        a = File("f.a")
        b1 = File("f.b1")
        b2 = File("f.b2")
        preprocess_job = Job("preprocess")\
                            .add_args("-i", a, "-o", b1, "-o", b2)\
                            .add_inputs(a)\
                            .add_outputs(b1, b2, stage_out=False, register_replica=False)\
                            .add_profiles(Namespace.PEGASUS, key="label", value="cluster-1")

        # Add left Findrange job
        c1 = File("f.c1")
        findrange_left_job = Job("findrange")\
                                .add_args("-i", b1, "-o", c1)\
                                .add_inputs(b1)\
                                .add_outputs(c1, stage_out=False, register_replica=False)\
                                .add_profiles(Namespace.PEGASUS, key="label", value="cluster-1")
        
        # Add right Findrange job
        c2 = File("f.c2")
        findrange_right_job = Job("findrange")\
                                .add_args("-i", b2, "-o", c2)\
                                .add_inputs(b2)\
                                .add_outputs(c2, stage_out=False, register_replica=False)\
                                .add_profiles(Namespace.PEGASUS, key="label", value="cluster-1")

        # Add Analyze job
        d = File("f.d")
        analyze_job = Job("analyze")\
                        .add_args("-i", c1, "-i", c2, "-o", d)\
                        .add_inputs(c1, c2)\
                        .add_outputs(d, stage_out=True, register_replica=True)\
                        .add_profiles(Namespace.PEGASUS, key="label", value="cluster-1")
        
        self.wf.add_jobs(preprocess_job, findrange_left_job, findrange_right_job, analyze_job)


if __name__ == '__main__':
    parser = ArgumentParser(description="Pegasus Diamond Workflow")

    parser.add_argument("-s", "--skip_sites_catalog", action="store_true", help="Skip site catalog creation")
    parser.add_argument("-e", "--execution_site_name", metavar="STR", type=str, default="condorpool", help="Execution site name (default: condorpool)")
    parser.add_argument("-o", "--output", metavar="STR", type=str, default="workflow.yml", help="Output file (default: workflow.yml)")

    args = parser.parse_args()
    
    workflow = DiamondWorkflow(args.output)

    if not args.skip_sites_catalog:
        print("Creating execution sites...")
        workflow.create_sites_catalog(args.execution_site_name)

    print("Creating workflow properties...")
    workflow.create_pegasus_properties()
    
    print("Creating transformation catalog...")
    workflow.create_transformation_catalog(args.execution_site_name)

    print("Creating replica catalog...")
    workflow.create_replica_catalog()

    print("Creating diamond workflow dag...")
    workflow.create_workflow()

    workflow.write()
