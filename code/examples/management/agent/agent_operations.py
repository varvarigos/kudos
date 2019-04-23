
"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


import json
import psutil
import netifaces
import subprocess


def inventory(level):

	response = { "success": True , "output": { "hardware": {} , "software": [] } }

	if level == 0 : # hardware inventory
		response["output"]["hardware"] = hardware()
	elif level == 1:  # software inventory
		response["output"]["software"] = software()
	else: # both hardware & software
		response["output"]["hardware"] = hardware()
		response["output"]["software"] = software()

	return response


def hardware():

	details = {}

	result = subprocess.run("uname -n", universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	details["machine_name"] = result.stdout.strip(" \n\t")

	memory = psutil.virtual_memory()
	total_memory_mb = int(memory.total)/1024
	free_memory_mb = int(memory.free)/1024
	used_memory_mb = total_memory_mb - free_memory_mb

	memory_utilization = round(float(used_memory_mb)/float(total_memory_mb)*100,2)

	disk = psutil.disk_usage("/")
	
	details["total_disk_GB"] = round((disk[0]/1024/1024/1024), 2)
	details["disk_utilization"] = disk[3]
	details["cpu_cores"] = int(psutil.cpu_count())
	details["cpu_utilization"] = psutil.cpu_percent(interval=1)
	details["total_memory_MB"] = total_memory_mb
	details["memory_utilization"] = memory_utilization
	details["network_interfaces"] = {}

	for iface in netifaces.interfaces():
		addrs = netifaces.ifaddresses(iface)
		details["network_interfaces"][iface] = { "AF_INET": "", "AF_LINK": "" }
		if netifaces.AF_INET in addrs :
			details["network_interfaces"][iface]["AF_INET"] = addrs[netifaces.AF_INET]
		if netifaces.AF_LINK in addrs :
			details["network_interfaces"][iface]["AF_LINK"] = addrs[netifaces.AF_LINK]

	return details

def software():


	installed_packages = []

	packages = subprocess.run("dpkg --get-selections | grep -v deinstall", universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	for package in packages.stdout.split("\n")[:-1]:
		installed_packages.append(package.split("\t")[0])

	return installed_packages


def execute_shell_command(cmd_and_parameters):

	result = subprocess.run("%s"%(cmd_and_parameters), universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	if result.returncode > 0 :
		return { "success": False , "output": result.stderr }
	else:
		return { "success": True , "output": result.stdout }


def execute_simple_command(cmd_and_parameters):

	arguments = cmd_and_parameters.split(" ")

	try:
		subprocess.Popen(arguments)
		return { "success": True , "output": { } }
	except:
		return { "success": False , "output": { } }


def install_package(package):

	result = subprocess.run("apt-get -y install %s"%(package), universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	if result.returncode > 0 :
		return { "success": False , "output": result.stderr }
	else:
		return { "success": True , "output": result.stdout }


def uninstall_package(package):

	result = subprocess.run("apt-get -y -q purge %s"%(package), universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	if result.returncode > 0 :
		return { "success": False , "output": result.stderr }
	else:
		return { "success": True , "output": result.stdout }

