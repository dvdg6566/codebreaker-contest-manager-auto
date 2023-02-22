'''
SANDBOX EXECUTION OF CODE FILES
-------------------------------

Runs specified command as Python Subprocess (Popen) 
Regularly uses psutil to query process time and memory to prevent lambda execution fails
Returns runtime, memory and statuscode
'''

import os
import signal
import psutil
import resource
import subprocess
from math import ceil
from time import sleep, monotonic

def execute(cmd, outputFile, timeLimit, memoryLimit, checker=0):
	for proc in psutil.process_iter():
		if proc.name() == 'code':
			pid = proc.pid
			os.kill(pid, signal.SIGTERM)

	# Hard limits for execution
	allocatedTime = ceil(timeLimit+0.5)
	allocatedMemory = (memoryLimit+128) * 1024 * 1024
	numConnections = len(psutil.net_connections())

	def setLimits():
		if not checker:
			resource.setrlimit(resource.RLIMIT_NOFILE, (4,4))
		
	with open(outputFile,"wb") as out:
		if not checker: 
			process = subprocess.Popen(cmd, shell=True, stdout=out, stderr = subprocess.PIPE,preexec_fn = setLimits)
		else:
			process = subprocess.Popen(cmd, shell=True, stdout=out, stderr = subprocess.PIPE)
	
	pid = process.pid
	p = psutil.Process(pid)
	verdict = 'AC'

	memory = 0
	time = 0
	initial_wall_time = monotonic()

	while True:
		if process.poll() is not None:
			# Check if the process has finished
			break
		try:
			# Gets time and memory of certain PID
			# p is the sh process (that's running ./code)
			# child is the code process (the actual code invocation)
	
			children = p.children(recursive=True)
			
			# Many children: Fork Bomb
			if len(children) > 1:
				process.terminate()
				for child in children:
					child.terminate()
				break
				
			if len(children) == 1: 
				child = children[0]

				wall_time = monotonic() - initial_wall_time

				memory = max(child.memory_info().vms, memory)
				time = max(child.cpu_times().user, time)
				
				if wall_time > 20: 
					process.terminate()
					break

			if time > allocatedTime:
				process.terminate()
				break

			if memory > allocatedMemory:
				process.terminate()
				break

		except Exception as e:
			break
		# sleep(0.01)
	
	process.wait()
	returncode = abs(process.returncode)

	if time > timeLimit:
		verdict = 'TLE'
	elif memory > memoryLimit * 1024 * 1024:
		verdict = 'MLE'
	elif returncode != 0:
		verdict = "RTE"

	result = {
		"verdict": verdict,
		"score":0,
		"runtime": round(time, 3),
		"memory": round(memory / 1024 / 1024, 1), 
		"returnCode":returncode
	}

	return result