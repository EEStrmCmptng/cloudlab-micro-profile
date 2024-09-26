"""This is a trivial example of a gitrepo-based profile; The profile source code and other software, documentation, etc. are stored in in a publicly accessible GIT repository (say, github.com). When you instantiate this profile, the repository is cloned to all of the nodes in your experiment, to `/local/repository`. 

This particular profile is a simple example of using a single raw PC. It can be instantiated on any cluster; the node will boot the default operating system, which is typically a recent version of Ubuntu.

Instructions:
Wait for the profile instance to start, then click on the node in the topology and choose the `shell` menu item. 
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Emulab extensions.
import geni.rspec.emulab as emulab

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Default ubuntu image
ubuntu_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD'

pc.defineParameter("dataset", "Your dataset URN",
                   portal.ParameterType.STRING,
                   "urn:publicid:IDN+apt.emulab.net:bayopsys-pg0+imdataset+EEFlinkMicro")

pc.defineParameter("mountpoint", "Mountpoint for file system",
                   portal.ParameterType.STRING, "/mydata")

pc.defineParameter("phystype",
                    "Physical Node Type",
                    portal.ParameterType.STRING,
                    "c6220")

pc.defineParameter("sameSwitch",  "No Interswitch Links", portal.ParameterType.BOOLEAN, False,
                    advanced=True,
                    longDescription="Sometimes you want all the nodes connected to the same switch. " +
                    "This option will ask the resource mapper to do that, although it might make " +
                    "it imppossible to find a solution. Do not use this unless you are sure you need it!")

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()
pc.verifyParameters()

# Add a raw PC to the request.
node = request.RawPC("mynode")
node.disk_image = ubuntu_image
node.hardware_type = params.phystype
node_bs = node.Blockstore("bs", params.mountpoint)
node_bs.dataset = params.dataset

# Install and execute a script that is contained in the repository.
node.addService(pg.Execute(shell="bash", command="/local/repository/silly.sh"))

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
