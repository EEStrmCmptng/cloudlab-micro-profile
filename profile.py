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

# Optional link speed, normally the resource mapper will choose for you based on node availability
pc.defineParameter("linkSpeed", "Link Speed",portal.ParameterType.INTEGER, 0,
                   [(0,"Any"),(100000,"100Mb/s"),(1000000,"1Gb/s"),(10000000,"10Gb/s"),(25000000,"25Gb/s"), (40000000,"40Gb/s"), (100000000,"100Gb/s")],
                   advanced=True,
                   longDescription="A specific link speed to use for your lan. Normally the resource " +
                   "mapper will choose for you based on node availability and the optional physical type.")

pc.defineParameter("sameSwitch",  "No Interswitch Links", portal.ParameterType.BOOLEAN, False,
                    advanced=True,
                    longDescription="Sometimes you want all the nodes connected to the same switch. " +
                    "This option will ask the resource mapper to do that, although it might make " +
                    "it imppossible to find a solution. Do not use this unless you are sure you need it!")

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()
pc.verifyParameters()

# IP [10.10.1.1, 10.10.1.2, 10.10.1.3, 10.10.1.4]
#JobManager10-1, Source10-2, Mapper10-3, Sink10-4

# Create link/lan.
lan = request.LAN()
if params.linkSpeed > 0:
    lan.bandwidth = params.linkSpeed
if params.sameSwitch:
    lan.setNoInterSwitchLinks()
    
# JobManager node
node1 = request.RawPC("JobManager10-1")
node1.disk_image = ubuntu_image
node1.hardware_type = params.phystype
node1_bs = node1.Blockstore("bs", params.mountpoint)
node1_bs.dataset = params.dataset
iface1 = node1.addInterface()
iface1.addAddress(pg.IPv4Address("10.10.1.1", "255.255.255.0"))
lan.addInterface(iface1)
    
# Source node
node2 = request.RawPC("Source10-2")
node2.disk_image = ubuntu_image
node2.hardware_type = params.phystype
iface2 = node2.addInterface()
iface2.addAddress(pg.IPv4Address("10.10.1.2", "255.255.255.0"))
lan.addInterface(iface2)

# Install and execute a script that is contained in the repository.
#node1.addService(pg.Execute(shell="bash", command="/local/repository/silly.sh"))

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
