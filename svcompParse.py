# Switch to llsplatInitInput

import os,sys
import subprocess
import time
import datetime
import pdb
import re

VERIFICATION_TOOL = {'klee', 'llsplat', 'crest'}
#CRESTC='/home/mingao/workspace/crest-project/crest/bin/crestc'
#RUNCREST='/home/mingao/workspace/crest-project/crest/bin/run_crest'
CRESTC='/home/mingao/Projects/crest-project/bin/crestc'
RUNCREST='/home/mingao/Projects/crest-project/bin/run_crest'
KLEE='/home/mingao/Projects/klee-3.4-release-project/klee/Release+Asserts/bin'
MAXITER="Def"
TOTALBRANCH=""
TOTALLINE=0
CREST_METHOD=""
KLEE_ARGUMENT=""
LLSPLAT_ARGUMENT=""
REPORTFILE=""
RUNTOOL=0


def initReportFile(filename):
	fp_rep = open(filename,"w")
	fp_rep.write("FILENAME\tLOC\tCURRENT ITER\tBRANCH COVERED\tTOTAL BRANCHES\tBRANCH COVERAGE\tRUN TIME\n")	
	fp_rep.close()

def clearFolder():
	list_dirs = os.walk('./')
	for root,dirs,files in list_dirs:
		for name in dirs:
			subprocess.call("rm -rf "+os.path.join(root, name), shell=True)
	
########################################################
###              Update Result File
########################################################

def writeToReportTimeout(file_name):
	fp_rep = open("../"+REPORTFILE,"a")
	fp_rep.write(file_name+'\t\t'+'TimeOut\n')
	fp_rep.close()

def parseCrestTotalBranchFile():
	global TOTALBRANCH

	fp_to = open("total_branch.log","r")
	for line in fp_to:
		splited_str_arr = line.split()
		if len(splited_str_arr) >=2 and splited_str_arr[0] == 'Read' and splited_str_arr[2] == 'branches.': 		
			TOTALBRANCH = splited_str_arr[1]
	fp_to.close()

def parseCrestLogFile(log_file_name, file_name, run_time):
	global TOTALBRANCH
	global TOTALLINE
	time.sleep(5)	
	fp_log = open(log_file_name, "r")
	fp_rep = open("../"+REPORTFILE,"a")
	flag = 0;	
	for line in fp_log:
		
		if "Iteration " in line: 
			print (line)			
			flag = 1			
			splited_str_arr = line.split()
			current_iter = splited_str_arr[1]
			covered_br = splited_str_arr[4]
			coverage_br = str(float('%.4f' %(int(covered_br)/int(TOTALBRANCH)))*100)+'%'
	
	if (flag == 1):	
		fp_rep.write(file_name+'\t'+str(TOTALLINE)+'\t'+current_iter+'\t'+covered_br+'\t'+TOTALBRANCH+'\t'+coverage_br+'\t'+str(run_time)+'\n')
						
	if (flag == 0):
		fp_rep.write(file_name+'\t'+str(TOTALLINE)+'\t\tERROR\n')

	fp_log.close()
	fp_rep.close()

def parseKleeLast(file_name, run_time):
	global TOTALBRANCH
	global TOTALLINE
	fp_rep = open("../"+REPORTFILE,"a")

	if os.path.isfile("./klee-last/run.stats"):
		fp_log = open("./klee-last/run.stats", "r")
		
		for line in fp_log:
			pass
		last = line
		splited_str_arr = last.split(',')
		TOTALBRANCH = str(int(splited_str_arr[3])*2 - 34)
		covered_br = str(int(splited_str_arr[1])*2+	int(splited_str_arr[2]))
		coverage_br = str(float('%.4f' %(int(covered_br)/int(TOTALBRANCH)))*100)+'%'
		fp_rep.write(file_name+'\t'+str(TOTALLINE)+'\t'+covered_br+'\t'+TOTALBRANCH+'\t'+coverage_br+'\t'+str(run_time)+'\n')
		fp_log.close()
	else:
		fp_rep.write(file_name+'\t'+str(TOTALLINE)+'\t\tError\n')	

	fp_rep.close()

def parseLlsplatFile(log_file_name, file_name, run_time):
	global TOTALBANCH
	global TOTALLINE
	fp_log = open(log_file_name, "r")
	fp_rep = open("../"+REPORTFILE,"a")
	flag = 0
	for line in fp_log:
		if "runs" in line:
			flag = 1
			splited_str_arr = line.split()
			current_iter = splited_str_arr[2]
		if "covered" in line and "branches out of" in line:
			flag = 1 
			splited_str_arr = line.split()
			covered_br = splited_str_arr[1]
			TOTALBRANCH = splited_str_arr[5]
			coverage_br = str(float('%.4f' %(int(covered_br)/int(TOTALBRANCH)))*100)+'%'
			break

	if (flag == 1):
		fp_rep.write(file_name+'\t'+str(TOTALLINE)+'\t'+current_iter+'\t'+covered_br+'\t'+TOTALBRANCH+'\t'+coverage_br+'\t'+str(run_time)+'\n')

	if (flag == 0):
		fp_rep.write(file_name+'\t'+str(TOTALLINE)+'\t\tERROR\n')		

	fp_log.close()
	fp_rep.close()


########################################################
###        Replace Source and Run Tool
########################################################

def replaceAndRun(input_file, v_tool, max_time):
	global TOTALLINE

	TYPE_NAME = {'int','long','short','char'}
	EQUAL = '='
	flag = 0
	input_file_name = input_file+'.c'

	if v_tool not in VERIFICATION_TOOL:
		assert 0, "unknown verification tool name"

	output_file_name = input_file +'__mod__'+'.c'

	fp_read=open(input_file_name, "r")
	fp_write=open(output_file_name, "w")

	old_line = ''
	new_line = ''

	if v_tool == 'llsplat':
		fp_write.write('''#include "instrument.h"\n''')
	elif v_tool == 'crest':
		fp_write.write('''#include <crest.h>\n''')
	elif v_tool == 'klee':
		fp_write.write('\n')



	TOTALLINE = 0
	for line in fp_read:
		TOTALLINE = TOTALLINE + 1
		splited_str_arr = line.split()
		if v_tool == 'llsplat' and re.search('\w*\s+main\s*\(.*\s*', line):
			print ("Here\n")
			flag = 1 
			line = line.replace("main", "llsplatInstrumented")			
			fp_write.write(line)

		for splited_str in splited_str_arr:
			if "#line" in splited_str:
				flag = 1
				break
		      
			if "VERIFIER_error" in splited_str:
				flag = 1
				if ("ERROR:" in splited_str_arr[0]):
					new_line = "ERROR:\n"
					fp_write.write(new_line)
					break
		              
			if "VERIFIER_nondet_" in splited_str:
				flag = 1            
				# int a = nondet;				
				if (splited_str_arr[0] in TYPE_NAME and splited_str_arr[1] != splited_str):                
					if v_tool == 'llsplat':
						new_line = splited_str_arr[0]+' '+splited_str_arr[1]+';'+'\n'+'llsplatInitInput((address_t)&'+splited_str_arr[1]+');'+'\n'
					elif v_tool == 'crest':

						if 'unsigned' not in line:
							CREST_MACRO = 'CREST_'
						else:
							CREST_MACRO = 'CREST_unsigned_'

						if 'long' in splited_str:
							new_line = splited_str_arr[0]+' '+splited_str_arr[1]+';'+'\n'+CREST_MACRO+'int'+'('+splited_str_arr[1]+');'+'\n'
						else:
							new_line = splited_str_arr[0]+' '+splited_str_arr[1]+';'+'\n'+CREST_MACRO+splited_str_arr[0]+'('+splited_str_arr[1]+');'+'\n'
					elif v_tool == 'klee':
						new_line = splited_str_arr[0]+' '+splited_str_arr[1]+';'+'\n'+'klee_make_symbolic(&'+splited_str_arr[1]+', sizeof('+splited_str_arr[1]+'), "'+splited_str_arr[1]+'");\n'

					fp_write.write(new_line)

					break;
				#{ int a = non_det;
				elif (splited_str_arr[1] in TYPE_NAME and splited_str_arr[2] != splited_str):                

					if v_tool == 'llsplat':
						new_line = splited_str_arr[0]+' '+splited_str_arr[1]+' '+splited_str_arr[2]+';'+'\n'+'llsplatInitInput((address_t)&'+splited_str_arr[2]+');'+'\n'
					elif v_tool == 'crest':
						if 'unsigned' not in line:
							CREST_MACRO = 'CREST_'
						else:
							CREST_MACRO = 'CREST_unsigned_'

						if 'long' in splited_str:
							new_line = splited_str_arr[0]+' '+splited_str_arr[1]+' '+splited_str_arr[2]+';'+'\n'+CREST_MACRO+'int'+'('+splited_str_arr[2]+');'+'\n'
						else:
							new_line = splited_str_arr[0]+' '+splited_str_arr[1]+' '+splited_str_arr[2]+';'+'\n'+CREST_MACRO+splited_str_arr[1]+'('+splited_str_arr[2]+');'+'\n'
					elif v_tool =='klee':
						new_line = splited_str_arr[0]+' '+splited_str_arr[1]+' '+splited_str_arr[2]+';'+'\n'+'klee_make_symbolic(&'+splited_str_arr[2]+', sizeof('+splited_str_arr[2]+'), "'+splited_str_arr[2]+'");\n'
					
					fp_write.write(new_line)
					break;                
				#a = non_det
				elif (splited_str_arr[1] == EQUAL):
					if v_tool == 'llsplat':
						new_line = 'llsplatInitInput((address_t)&'+splited_str_arr[0]+');'+'\n'
					elif v_tool == 'crest':
						splited_str_type = splited_str.split('_')													
						if 'long' in splited_str:
							new_line = 'CREST_'+'int'+'('+splited_str_arr[0]+');'+'\n'
						else:	
							new_line = 'CREST_'+splited_str_type[4].split('(')[0]+'('+splited_str_arr[0]+');'+'\n'						
					elif v_tool == 'klee':
						new_line ='klee_make_symbolic(&'+splited_str_arr[0]+', sizeof('+splited_str_arr[0]+'), "'+splited_str_arr[0]+'");\n'
					fp_write.write(new_line)
					break;

		
		                             
		if (flag == 0):
			fp_write.write(line)
		else:
			flag = 0;            

	fp_read.close()
	fp_write.close()

	if RUNTOOL==1:	
		os.system('rm -rf '+input_file)
		os.system('mkdir '+input_file)
		os.system('cp '+input_file_name+' ./'+input_file)
		os.system('mv '+output_file_name+' ./'+input_file)	
		if v_tool == 'llsplat':
			os.system('cp Makefile ./'+input_file)	
		os.chdir(input_file)
	
		filename, file_ext = os.path.splitext(output_file_name)		
		if v_tool == 'crest':
			try:		
				subprocess.call(CRESTC+' '+output_file_name+' 2>total_branch.log',shell=True)
				start = time.time()			
				subprocess.call(RUNCREST+' ./'+input_file+'__mod__ '+MAXITER+' '+CREST_METHOD+' 2>result_'+input_file+'.log', timeout=max_time, shell = True)
				end = time.time()
			except subprocess.TimeoutExpired:
				end = time.time()		
			parseCrestTotalBranchFile()
			parseCrestLogFile('result_'+input_file+'.log', input_file, round(end-start,3))
	
		if v_tool == 'klee':
			try:
				subprocess.call('/home/mingao/Projects/klee-3.4-dbg-project/llvm-3.4/install/bin/clang -emit-llvm -c -g '+output_file_name, shell=True)
				start = time.time()			
				proc1=subprocess.call(KLEE+' '+KLEE_ARGUMENT+' '+filename+'.bc', shell=True)					
				end = time.time()
			except subprocess.TimeoutExpired:
				ps = subprocess.Popen(('ps', '-A'), stdout=subprocess.PIPE)
				output = subprocess.check_output(('grep', 'klee'), stdin=ps.stdout)
				ps.wait()
				print (output)
				if ('klee' in str(output, encoding='utf8')):
					out_split = str(output,encoding='utf8').split()
					PID = out_split[0]
					print(PID)				
					subprocess.call('kill '+PID, shell = True)
				#pdb.set_trace()			
				print(filename+" TimeOut\n")
				writeToReportTimeout(input_file)
				os.chdir('..')
				return				
			parseKleeLast(input_file, round(end-start,3))

		if v_tool == 'llsplat':
			try:
				#pdb.set_trace()	
				subprocess.call('make TARGET='+filename, shell=True)
				start = time.time()			
				subprocess.call('./llsplat-'+filename+'.exe'+' '+LLSPLAT_ARGUMENT+' '+filename+' 2>'+filename+'.log', timeout=max_time, shell=True)
				end = time.time()
			except subprocess.TimeoutExpired:
				print(filename+" TimeOut\n")
				writeToReportTimeout(input_file)
				os.chdir('..')
				return
			parseLlsplatFile(filename+'.log', filename, round(end-start,3))
		os.chdir('..')


def getLlsplatMaxIter(argument):
	arg_list=argument.split()
	for arg in arg_list:	
		if "-max-iter=" in arg:
			iter_list=arg.split("=")
			return iter_list[-1]
	return "DefaultIter"


########################################################
###        						Main Function
########################################################	
def process(argv, max_time):
	global MAXITER
	global TOTALBRANCH
	global TOTALLINE
	global CREST_METHOD
	global KLEE_ARGUMENT
	global LLSPLAT_ARGUMENT
	global REPORTFILE
	v_tool = argv[1]
	clearFolder()

	if v_tool == 'crest':
		MAXITER=argv[2]
		CREST_METHOD=argv[3]
	if v_tool == 'klee' and len(argv) >= 3:
		KLEE_ARGUMENT = argv[2]
	if v_tool == 'llsplat' and len(argv) >= 3:
		LLSPLAT_ARGUMENT = argv[2]
		MAXITER=getLlsplatMaxIter(LLSPLAT_ARGUMENT)

	REPORTFILE = "report_"+v_tool+'_'+MAXITER+'_'+datetime.datetime.now().strftime("%m%d%H%M")+'.csv'
	initReportFile(REPORTFILE)


	list_dirs = os.walk('./')
	for root,dirs,files in list_dirs:
		for f in files:
			filename, file_ext = os.path.splitext(f)
			if len(filename) > 30:
				filename=filename[0:29]
				new_file_name= filename+file_ext
				os.system("mv "+f+" ./"+new_file_name)
			if file_ext == '.c' and '__mod__' not in f:
				print ('Start Processing'+filename)
				replaceAndRun(filename, v_tool, max_time)
				print ('Done Processing'+filename)

	if v_tool == 'klee':
		try:
			ps = subprocess.Popen(('ps', '-A'), stdout=subprocess.PIPE)
			output = subprocess.check_output(('grep', 'klee'), stdin=ps.stdout, stderr=subprocess.STDOUT)
			ps.wait()
			print (output)
			if ('klee' in str(output, encoding='utf8')):
				out_split = str(output,encoding='utf8').split()
				PID = out_split[0]
				print(PID)				
				subprocess.call('kill '+PID, shell = True)
		except subprocess.CalledProcessError:
			pass

#clearFolder()

def main():
	v_tool = sys.argv[1]
	argument = ["script"]
	argument.append(v_tool)
	if v_tool == 'crest':
		argument.append("6000000")
		argument.append("-dfs")		
		process(argument, 6000)
	elif v_tool == 'klee':	
		argument.append("-max-time="+str(120))
		process(argument, 6000)
	elif v_tool == 'llsplat':
		argument.append('''-bmc -max-iter=6000000 -max-len=50''')
		process(argument, 6000)
	
if __name__ == "__main__":
	main()
			 
