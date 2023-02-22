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

# Gets time and memory of certain PID
# p is the sh process (that's running ./code)
# child is the code process (the actual code invocation)
def getMemory(p):
	if (len(p.children()) == 0): return 0
	child = p.children()[0]
	
	memory_info = child.memory_info()
	# TODO: Determine if RMS or VMS is more suitable indicator
	return memory_info.vms

def getTotalTime(p):
	if (len(p.children()) == 0): return 0
	child = p.children()[0]
	
	time_info = child.cpu_times()
	return time_info.user
	# return monotonic()

def execute(cmd, outputFile, timeLimit, memoryLimit):

	for proc in psutil.process_iter():
		if proc.name() == 'code':
			pid = proc.pid
			os.kill(pid, signal.SIGTERM)

	# Hard limits for execution
	allocatedTime = ceil(timeLimit+0.5)
	allocatedMemory = (memoryLimit+128) * 1024 * 1024
	numConnections = len(psutil.net_connections())

	if outputFile != None:
		with open(outputFile,"wb") as out:
			process = subprocess.Popen(cmd, shell=True, stdout=out, stderr = subprocess.PIPE)
	else:
		process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)

	pid = process.pid
	p = psutil.Process(pid)
	# p.rlimit(psutil.RLIMIT_FSIZE, (0,0))
	sleep(0.1)
	verdict = 'AC'

	memory = 0
	time = 0

	initTime = getTotalTime(p)

	while True:
		if process.poll() is not None:
			# Check if the process has finished
			break
		try:
			current_memory = getMemory(p)
			current_time = getTotalTime(p)

			memory = max(current_memory, memory)
			time = max(current_time, time) - initTime

			if time > allocatedTime:
				process.terminate()
				process.wait()
				break

			if memory > allocatedMemory:
				process.terminate()
				process.wait()
				break

		except Exception as e:
			print(e)
			break
		sleep(0.01)
	
	# HTTP request was made
	if len(psutil.net_connections()) > numConnections:
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