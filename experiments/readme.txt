This repository contains data that was used and obtained from experiments conducted in the paper:
"Multiplicative Incentive Mechanisms For High-Quality Crowdsourced Data" by Nihar B. Shah and Dengyong Zhou.

There are nine folders containing the data from the nine different experiments, with each folder containing:
- three ".html" files depicting the interface shown to the workers under the three mechanisms
- a folder called "source" containing the source images or audio files pertaining the task
- a file whose name ends as "_true.csv" containing the ground truth for the questions in that experiment
- three other ".csv" files containing the raw data obtained from the workers

There is also a file called "analysis.py", which is a python script for analysis of the data and construction of the plots presented in the paper. To analyze the data from any specific experiment, in the first line of the script, set the string variable "EXPERIMENT_TYPE" to one of the following: 'Bridges','licencePlatesTranscribe','Dogs','headsOfCountries','Flags','Textures','shakespeareTranscribe','filmImageTranscribe','TTStranscribe'.

Finally, note that the questions are numbered '1,2,...' in the html files (shown to the workers), the csv file numbers the corresponding answers as '0,1,...' (used by the script).