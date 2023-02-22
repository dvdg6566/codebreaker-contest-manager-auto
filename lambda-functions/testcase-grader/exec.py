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

def execute(cmd, outputFile, timeLimit, memoryLimit, openFileLimit=100):
	for proc in psutil.process_iter():
		if proc.name() == 'code':
			pid = proc.pid
			os.kill(pid, signal.SIGTERM)

	# Hard limits for execution
	allocatedTime = ceil(timeLimit+0.5)
	allocatedMemory = (memoryLimit+128) * 1024 * 1024
	numConnections = len(psutil.net_connections())

	with open(outputFile,"wb") as out:
		process = subprocess.Popen(cmd, shell=True, stdout=out, stderr = subprocess.PIPE)
	
	pid = process.pid
	p = psutil.Process(pid)
	# p.rlimit(psutil.RLIMIT_FSIZE, (0,0))
	sleep(0.1)
	verdict = 'AC'

	memory = 0
	time = 0
	securityViolation = 0
	initial_wall_time = monotonic()

	while True:
		if process.poll() is not None:
			# Check if the process has finished
			break
		try:
			if len(psutil.net_connections()) > numConnections:
				securityViolation = True
				process.terminate()
				break

			# Gets time and memory of certain PID
			# p is the sh process (that's running ./code)
			# child is the code process (the actual code invocation)

			if (len(p.children()) != 0): 
				child = p.children()[0]
				if len(child.open_files()) > openFileLimit:
					securityViolation = True
					process.terminate()
					break

				wall_time = monotonic() - initial_wall_time

				memory = max(child.memory_info().vms, memory)
				time = max(child.cpu_times().user, time)

			if time > allocatedTime or wall_time > 20:
				process.terminate()
				break

			if memory > allocatedMemory:
				process.terminate()
				break

		except Exception as e:
			print(e)
			break
		# sleep(0.01)
	
	# HTTP request was made or extra file was written to
	if securityViolation:
		return {
			"verdict": "Security Violation",
			"score": 0,
			"runtime": 0,
			"memory": 0,
			"returnCode": 0
		}
	
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