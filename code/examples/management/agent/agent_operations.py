
"""
	Authors: Andreas Varvarigos ( andreas.varvarigos@yahoo.com ) , Anastasis Varvarigos ( anastasis.varvarigos@gmail.com )
	License: GPL 3.0
	Athens March 2019
"""


import json
import psutil
import netifaces
import subprocess

"""
  Εκτελεί και επιστρέφει τα αποτελέσματα καταγραφής (υλικού, λογισμικού , πληρης) ανάλογα με την παράμετρο
"""
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

"""
  Συγκεντρώνει τις βασικές πληροφορίες για την κατάσταση του μηχανήματος κάνοντας χρήση της βιβλιοθήκης psutil 
  και εκτελώντας εντολές.
"""
def hardware():

	details = {}

	#Εκτελεί την εντολή uname -n , για να πάρει το όνομα του μηχανήματος
	result = subprocess.run("uname -n", universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	details["machine_name"] = result.stdout.strip(" \n\t")

	#Μέσω της psutil συγκεντρώνουμε όλες τις απαραίτητες λεπτομέρειες σχετικά με την μνήμη (RAM)
	memory = psutil.virtual_memory()
	total_memory_mb = int(memory.total)/1024
	free_memory_mb = int(memory.free)/1024
	used_memory_mb = total_memory_mb - free_memory_mb

	memory_utilization = round(float(used_memory_mb)/float(total_memory_mb)*100,2)

	# Μέσω της psutil συγκεντρώνουμε όλες τις απαραίτητες λεπτομέρειες σχετικά με τον διαθέσιμο αποθηκευτικό χώρο 
	disk = psutil.disk_usage("/")
	
	details["total_disk_GB"] = round((disk[0]/1024/1024/1024), 2)
	details["disk_utilization"] = disk[3]
	details["cpu_cores"] = int(psutil.cpu_count())
	details["cpu_utilization"] = psutil.cpu_percent(interval=1)
	details["total_memory_MB"] = total_memory_mb
	details["memory_utilization"] = memory_utilization
	details["network_interfaces"] = {}

	# Μέσω της netifaces, βρίσκουμε τις λεπτομέρειες για τις διαθέσιμες δικτυακές 
	for iface in netifaces.interfaces():
		addrs = netifaces.ifaddresses(iface)
		details["network_interfaces"][iface] = { "AF_INET": "", "AF_LINK": "" }
		if netifaces.AF_INET in addrs :
			details["network_interfaces"][iface]["AF_INET"] = addrs[netifaces.AF_INET]
		if netifaces.AF_LINK in addrs :
			details["network_interfaces"][iface]["AF_LINK"] = addrs[netifaces.AF_LINK]

	return details


"""
  Συγκεντρώνει και επιστρέφει όλα τα πακέτα λογισμικού που έχουν εγκατασταθεί στο μηχάνημα.
"""
def software():


	installed_packages = []

	#Εκτελούμε την εντολή  dpkg με τις κατάλληλες παραμέτρους που μας επιστρέφει όλα τα διαθέσιμα πακέτα λογισμικού
	packages = subprocess.run("dpkg --get-selections | grep -v deinstall", universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	#Στην συνέχεια επεξεργαζόμαστε την έξοδο της εντολής και δημιουργούμε απο το κείμενο που μας επέστρεψε μια λίστα
	#με τα διαθέσιμα πακέτα λογισμικού
	for package in packages.stdout.split("\n")[:-1]:
		installed_packages.append(package.split("\t")[0])

	return installed_packages


"""
  Εκκελεί μια εντολή συστήματος και επιστρέφει την κατάσταση και στοχεία για την εκτέλεση
"""
def execute_shell_command(cmd_and_parameters):

	result = subprocess.run("%s"%(cmd_and_parameters), universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	if result.returncode > 0 :
		return { "success": False , "output": result.stderr }
	else:
		return { "success": True , "output": result.stdout }


"""
  Εκτελεί μια γενική εντολή και επιστρέφει την κατάσταση της εκτέλεσης
"""
def execute_simple_command(cmd_and_parameters):

	arguments = cmd_and_parameters.split(" ")

	try:
		subprocess.Popen(arguments)
		return { "success": True , "output": { } }
	except:
		return { "success": False , "output": { } }

"""
   Εγκαθιστά ένα νέο πακέτο λογισμικού και επιστρέφει την κατάσταση της εγκατάστασης 
"""
def install_package(package):

	#Για την εγκατάσταση εκτελούμε την εντολή apt-get με τις κατάλληλες παραμέτρους
	result = subprocess.run("apt-get -y install %s"%(package), universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	if result.returncode > 0 :
		return { "success": False , "output": result.stderr }
	else:
		return { "success": True , "output": result.stdout }

"""
   Απεγκαθιστά ένα νέο πακέτο λογισμικού και επιστρέφει την κατάσταση της εγκατάστασης 
"""
def uninstall_package(package):

	#Για την απεγκατάσταση εκτελούμε την εντολή apt-get με τις κατάλληλες παραμέτρους
	result = subprocess.run("apt-get -y -q purge %s"%(package), universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	if result.returncode > 0 :
		return { "success": False , "output": result.stderr }
	else:
		return { "success": True , "output": result.stdout }

