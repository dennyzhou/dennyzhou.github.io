EXPERIMENT_TYPE = 'headsOfCountries'
#EXPERIMENT_TYPE should be one out of: 'Bridges','licencePlatesTranscribe','Dogs','headsOfCountries','Flags','Textures','shakespeareTranscribe','filmImageTranscribe','TTStranscribe'

import csv, string, matplotlib.pyplot as plt, numpy, copy, random, scipy, scipy.stats #, win32com.client
import os, os.path#, os.listdirfrom os import listdir, from os.path import isfile, join

filenames=[]
payment_type=[]
payment_amount=[]
payment_scale=[]
num_gold = 0
fixed_pay = 0

filenames=['baseline','skip','confidence']
payment_type = ['+','*','*']
if EXPERIMENT_TYPE=='Bridges':
	payment_amount = [[0,0,1],[0,1,1.5],[0,.5,1,1.4,1.5]]
	payment_scale = [5,5.9,5.9]
	num_gold=3
	fixed_pay=3
elif EXPERIMENT_TYPE=='licencePlatesTranscribe':
	payment_amount = [[0,0,1],[0,1,3],[0,.5,1,1.95,2]]
	payment_scale = [10,   .62,  3.1]
	num_gold=4
	fixed_pay=4
elif EXPERIMENT_TYPE=='Dogs':
	payment_amount = [[0,0,1],[0,1,2],[0,.67,1,1.66,2]]
	payment_scale = [8,  .78,  .78]
	num_gold=7
	fixed_pay = 5
elif EXPERIMENT_TYPE=='headsOfCountries':
	payment_amount = [[0,0,1],[0,1,3],[0,.5,1,1.95,2]]
	payment_scale = [2.5,.25,1.3]
	num_gold = 4
	fixed_pay = 2
elif EXPERIMENT_TYPE=='Flags':
	payment_amount = [[0,0,1],[0,1,2],[0,.67,1,1.66,2]]
	payment_scale = [4,   .2,   .2]
	num_gold=8
	fixed_pay=4
elif EXPERIMENT_TYPE=='Textures':
	payment_amount = [[0,0,1],[0,1,2],[0,.67,1,1.66,2]]
	payment_scale = [10, 3.1, 3.1]
	num_gold=4
	fixed_pay=3
elif EXPERIMENT_TYPE=='shakespeareTranscribe':
	payment_amount = [[0,0,1],[0,1,3],[0,.5,1,1.95,2]]
	payment_scale = [20, 5.5, 12.5]
	num_gold=2
	fixed_pay=5
elif EXPERIMENT_TYPE=='filmImageTranscribe':
	payment_amount = [[0,0,1],[0,1,3],[0,.5,1,1.95,2]]
	payment_scale = [20,  5.5, 12.5]
	num_gold=2
	fixed_pay=5
elif EXPERIMENT_TYPE=='TTStranscribe':
	payment_amount = [[0,0,1],[0,1,3],[0,.5,1,1.95,2]]
	payment_scale = [20,  5.5, 12.5]
	num_gold=2
	fixed_pay=5

numpy.set_printoptions(precision=3,linewidth=300,suppress =True,threshold=10000)

class experiment_result:
	def __init__(self,csv_filename):
		self.csv_filename=csv_filename
		self.num_workers=1
		self.num_questions=1
		
		#record if this task was a multiple choice question task or a transcription task
		self.task_type='MCQ'
		if string.find(csv_filename.lower(),'transcribe') != -1:
			self.task_type='transcribe'

		#record if the setting was skip-based or confidence-based
		self.answer_type = 'skip'
		if string.find(csv_filename,'confidence') != -1:
			self.answer_type = 'confidence'

		csvfile = open(csv_filename+'.csv','r')
		reader = list(csv.reader(csvfile,delimiter=','))#,quotechar='')
		header = reader[0]
		reader.pop(0)		
		
		#obtain number of workers
		self.num_workers = len(reader)

		#obtain column number where actual answers start
		col_answers_start=-1
		for cols in header:
			col_answers_start += 1
			if cols[0:6]=='Answer':
				break
		#obtain number of questions	
		self.num_questions=0
		for cols in header:
			if cols[0:6]=='Answer' and cols[7].isdigit():	#the last condition detects if there are two separate "Answers" for each question: one containing the skip/confidence and the other containing the transcribed text
				self.num_questions += 1 
		
		if string.find(self.csv_filename,'baseline') == -1 and self.task_type=='transcribe':
			self.num_questions/=2
		
		#now that we have obtained num_workers and num_questions, we can initialize our matrices		
		self.answer_matrix=numpy.chararray((self.num_workers,self.num_questions),itemsize=100)
		self.true_labels = numpy.chararray(self.num_questions,itemsize=100)
		self.error_matrix=numpy.zeros((self.num_workers,self.num_questions))

		#READ AND EVALUATE ANSWERS
		if self.task_type=='transcribe':
			#Read True Labels		
			true_filename = csv_filename.split(' ')[0] + '_true'
			truefile = open(true_filename+'.csv','r')
			true_reader = list(csv.reader(truefile,delimiter=',',quotechar='\''))[0]

			for question in range(self.num_questions):
				self.true_labels[question] = true_reader[question].upper().replace(" ", "").translate(string.maketrans("",""), string.punctuation)
				
			#obtain answers and populate error_matrix
			reader = list(reader)
			#detect if there are two separate "Answers" for each question: one containing the skip/confidence and the other containing the transcribed text
			jump=2
			if string.find(self.csv_filename.lower(),'baseline')!=-1:
				jump=1
				
			for worker in range(self.num_workers):
				row = reader[worker]				
				for question in range(self.num_questions):
	    				if jump==2 and row[col_answers_start+2*question]=='':
						row[col_answers_start+2*question]='0:0'
					
					confidence=1
					answer = row[col_answers_start+question].upper().replace(" ", "").translate(string.maketrans("",""), string.punctuation)
					if jump==2:		
						confidence=(row[col_answers_start+2*question].split(':'))[1]
						answer = row[col_answers_start+2*question+1].upper().replace(" ", "").translate(string.maketrans("",""), string.punctuation)
						
					self.error_matrix[worker,question] = int(confidence)*(2*(answer==self.true_labels[question].upper())-1)
					if row[col_answers_start+jump*question]=='0':
						self.answer_matrix[worker,question] = ''
					else:
						self.answer_matrix[worker,question] = str(answer)+':'+str(confidence)
		else:
			#obtain answers and populate answer_matrix
			reader = list(reader)
			for worker in range(self.num_workers):
				row = reader[worker]
				for question in range(self.num_questions):
	    				if row[col_answers_start+question]=='':
					        row[col_answers_start+question]='0:0'
	    				temp=row[col_answers_start+question].split(':')
					self.answer_matrix[worker,question] = temp[1]
						
			#Read True Labels		
			true_filename = csv_filename.split(' ')[0] + '_true'
			truefile = open(true_filename+'.csv','r')
			true_reader = list(csv.reader(truefile,delimiter=',',quotechar='\''))[0]
			for question in range(self.num_questions):
				self.true_labels[question] = true_reader[question]
				
			def handleSpecialCases(trueORfalse,question,ans):
				global EXPERIMENT_TYPE
				if EXPERIMENT_TYPE=='Flags' and question==67 and ans=='C':
					return True
				else: 
					return trueORfalse

			for worker in range(self.num_workers):
				for question in range(self.num_questions):
					if self.answer_matrix[worker,question]!='0':
						trueORfalse=0
						if self.answer_type=='skip':
							trueORfalse = (self.answer_matrix[worker,question]==self.true_labels[question])
							trueORfalse = handleSpecialCases(trueORfalse,question,self.answer_matrix[worker,question])*1.0
						else:
							trueORfalse= (self.answer_matrix[worker,question][0]==self.true_labels[question])
							trueORfalse = handleSpecialCases(trueORfalse,question,self.answer_matrix[worker,question][0])*1.0
						
						if self.answer_type=='skip':
							self.error_matrix[worker,question]=trueORfalse*2-1
						else: #if self.answer_type=='confidence'
							self.error_matrix[worker,question]=(trueORfalse*2-1)*string.atoi(self.answer_matrix[worker,question][1])

	def fraction_in_error(self):	
		ret_fraction_attempted_in_error	=  numpy.sum(self.error_matrix<0)*1.0/numpy.sum(self.error_matrix!=0)
		ret_fraction_total_in_error	=  numpy.sum(self.error_matrix<0)*1.0/numpy.size(self.error_matrix)
		if self.answer_type=='confidence':
			ret_fraction_attempted_in_error =  numpy.sum(self.error_matrix<0)*1.0/numpy.sum(numpy.abs(self.error_matrix)!=0)
		return ret_fraction_attempted_in_error,ret_fraction_total_in_error

	def fraction_skipped(self):
		ans = numpy.sum(data[i].error_matrix==0)*1.0/(data[i].num_workers*data[i].num_questions)
		return ans
		
	def compute_bonus(self,p_type,p_amount,p_scale,gold_questions):
		bonus = numpy.zeros((self.num_workers))
		if p_type == '*':
			bonus+=1
		for w in range(self.num_workers):
			for q in gold_questions:
				if p_type=='*':
					bonus[w] *= p_amount[int(self.error_matrix[w,q]+(numpy.size(p_amount)-1)/2)]
				elif p_type=='+':
					bonus[w] += p_amount[int(self.error_matrix[w,q]+(numpy.size(p_amount)-1)/2)]
		bonus=numpy.clip(bonus,0,numpy.Inf)*p_scale
		return bonus
		
	def net_payment_via_random_sampling(self,p_type,p_amount,p_scale,fixed=0,num_gold=4):
		avg_bonus = numpy.zeros((self.num_workers))
    		num_iters=100
		for iter in range(num_iters):
			gold_questions = random.sample(numpy.arange(self.num_questions),num_gold)
			avg_bonus+=self.compute_bonus(p_type,p_amount,p_scale,gold_questions)+fixed
		avg_bonus=avg_bonus*1.0/num_iters
		return numpy.sum(avg_bonus)
			
	def levels_breakup(self,L=1):
		if self.answer_type!='confidence':
			L=1
		vals=numpy.zeros((2*L+1))
		for i in range(2*L+1):
			vals[i]=numpy.sum(self.error_matrix==i-L)
		return vals*1.0/(self.num_workers*self.num_questions)
	
fraction_attempted_in_error = numpy.zeros((len(filenames))) #number of questions with no errors
fraction_total_in_error = numpy.zeros((len(filenames))) #fraction of errors among answers attempted
fraction_skipped = numpy.zeros((len(filenames)))
bonus = numpy.zeros((len(filenames)))

data=list()
for i in range(len(filenames)):
	data.append(experiment_result('./'+EXPERIMENT_TYPE+'/'+EXPERIMENT_TYPE+' - '+filenames[i]))

for i in range(len(filenames)):
	fraction_attempted_in_error[i], fraction_total_in_error[i] = data[i].fraction_in_error()
	fraction_skipped[i] = data[i].fraction_skipped()
	bonus[i] = data[i].net_payment_via_random_sampling(payment_type[i],payment_amount[i],payment_scale[i],fixed_pay,num_gold)*1.0/data[i].num_workers

#PLOT STATISTICS FOR PAPER
rcParams['figure.figsize'] = 12,2.95#6*3.13,4*3.13
matplotlib.rcParams.update({'font.size': 14})

fig, axes = plt.subplots(nrows=1, ncols=4)
def draw_subplot_bar(values, ax, title=''):
	global filenames
	w=6
	plt.tight_layout()
	col=['#FFD1D1','#A9FFB5','#64DDFF']
	patterns = ('','','')#('//','*','...')
	bar_positions = numpy.arange(len(values))*w+.7
	if len(values)>3:
		col=['#44FFFF','#54EEFF','#64DDFF','#74CCFF','#84BBFF','#A9FFB5']
		patterns = ('\\','-','','++','//','...')
		bar_positions[5] += 5
	bars = ax.bar(bar_positions,values+.000001,w*.8,color=col)

	for bar, pattern in zip(bars, patterns):
		bar.set_hatch(pattern)
	yloc = plt.MaxNLocator(5)
	ax.yaxis.set_major_locator(yloc)
	ax.set_xticklabels(['']*len(filenames))
	ax.set_ylabel('\n\n\n ')
	ax.set_xticks([])
	ax.tick_params(axis='y',which='both',left='off',right='off',labelbottom='off')
all_plt_axes = iter(axes.flat)
    
draw_subplot_bar(fraction_total_in_error*100,all_plt_axes.next(),'% erroneous answers')
draw_subplot_bar(fraction_attempted_in_error*100,all_plt_axes.next(),'% erroneous among attempted')
draw_subplot_bar(bonus,all_plt_axes.next(),'Payment (cents)')
draw_subplot_bar(numpy.append(data[2].levels_breakup(2)*100, data[1].fraction_skipped()*100),all_plt_axes.next(),'')
plt.show()