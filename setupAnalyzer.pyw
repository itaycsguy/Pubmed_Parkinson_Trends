import os
import subprocess
import time

filename = os.path.dirname(os.path.abspath(__file__))+"\\setupAnalyzer.log"
append_write = 'w'
if os.path.exists(filename):
	append_write = 'a'
	
logfile = open(filename,append_write)

#Requirements:
##############

outputs = []
outputs.append([str(os.system("py -m pip install -U pip"))])#subprocess.call("py -m pip install -U pip"))
outputs[len(outputs)-1].append("py -m pip install -U pip")
outputs.append([str(os.system("py -m pip install numpy"))])#subprocess.call("py -m pip install numpy"))
outputs[len(outputs)-1].append("py -m pip install numpy")
outputs.append([str(os.system("py -m pip install xlsxwriter"))])#subprocess.call("py -m pip install xlsxwriter"))
outputs[len(outputs)-1].append("py -m pip install xlsxwriter")
outputs.append([str(os.system("py -m pip install progress"))])#subprocess.call("py -m pip install progress"))
outputs[len(outputs)-1].append("py -m pip install progress")
outputs.append([str(os.system("py -m pip install -U setuptool"))])#subprocess.call("py -m pip install -U setuptool"))
outputs[len(outputs)-1].append("py -m pip install -U setuptool")
outputs.append([str(os.system("py -m pip install matplotlib"))])#subprocess.call("py -m pip install matplotlib"))
outputs[len(outputs)-1].append("py -m pip install matplotlib")

logfile.write("[" + str(time.strftime("%d/%m/%y")) + "," + str(time.strftime("%H:%M:%S")) + "]" + "\n")

for output in outputs:
		logfile.write("Return Value= "+str(output[0])+" : Operation= "+str(output[1])+"\n")
logfile.close()


