import sys

# Class required for user-defined errors
class Error(Exception):
	pass #a null statement

# An error that is raised when there is an error with the user input arguments
class ArgumentError(Error):
	# initializes the error object
	def __init__(self, message):
		self.message = message

# An error that is raised when there are issues with a dictionary
class DictError(Error):
	# initializes the error object
	def __init__(self, message):
		# self.expression = expression
		self.message = message

# Takes in the files from argv and assigns them to the proper variable
# Inputs: file - the list of argv files 
# Returns: actualFile - pointer to the file actual.txt
#		   predictedFile - pointer to the file predicted.txt
#          windowNum - integer representing the window size
#          comparisonFile - pointer to comparison.txt which is open and given write permissions
def setFiles(files):
	# if there are too many or too few arguments, ArgumentError is raised
	if len(files) != 5:
		print('\n')
		raise ArgumentError("Program expects 4 arguments. {} arguments detected.".format(len(files) - 1))
	
	# Loops through the arguments and assigns each file to the correct variable
	for i in range(1,len(files)):
			if 'actual.txt' in files[i]:
				actualFile = files[i]
			elif 'predicted.txt' in files[i]:
				predictedFile = files[i]
			elif 'window.txt' in files[i]:
				#Reads file here to get the window size - converts the number to an int if it is not an int
				windowNum = int(open(files[i]).read())

				# Raises a value error if the window size is non-positive
				if windowNum < 1:
					raise ValueError("Window value must be a positive integer, value given: " + str(windowNum))
			elif 'comparison.txt' in files[i]:
				#Opens the file with write privilege so that output can be written to it
				comparisonFile = open(files[i], "w")

			# if the name of the file is incorrect, raise a ValueError
			else:
				raise ValueError("Input file: " + files[i] + " is not an allowed file name")

	# returns the 3 files and windowNum aka the window size
	return(actualFile, predictedFile, windowNum, comparisonFile)

# Creates a dictionary: 
# - if actual = False, creates a multilayered dictionary for the predicted values structured like so: {hour:{symbol:price, etc...}, hour2:{etc...} }
# - if actual = True, creates a dictionary that is structured like so: {hour: (sum, count), etc...} where sum is the sum of the price differences between the actual stock prices and the predicted stock prices and count is the number of differences that occur for that hour.
# Inputs: file - the file to be used for reading
#         dataDict - a dictionary object
#         actual - boolean used to determine the sort of dictionary to create, defualt value = False
#         pred - another dictionary object. Only set when actual = True. Default value = None
# Returns: dataDict - the created dictionary
def setDict(file,dataDict, actual=False, pred=None):
	fileHandler = open(file, 'r') # opens the file for reading

	#reads in each line of the text file
	for line in fileHandler:
		line = line.strip() #remove blank space and newline characters
		fields = line.split('|') #split line on '|' into list of inputs

		#make the code below easier to read to specify what each field stands for
		hour = int(fields[0]) 
		symbol = fields[1]
		price = float(fields[2])

		#creates this dictionary structure: {hour: {stock1: price1, stock2:price2, ...}, ...}
		if(actual==False): #i.e. if we are creating the dictionary for the predicted stock prices
			dataDict.setdefault(hour,{})[symbol] = price #creates multi-layered dictionary that first gets the hour, then the symbol, and this results in a predicted stock price

		#for the comparison dictionary creates this structure {hour: (sum, count), hour2: etc ...}
		else:
			if hour in pred: #checks if the hour is present in the predicted dictionary, if not, goes to else statement
				if symbol in pred[hour]: #further checks if the stock symbol is present in the predicted dictionary for this hour, if not, nothing is done
					loc = dataDict.get(hour, (0,0)) # gets the tuple from the current dictionary at the selected hour, if none exists returns the tuple (0,0) for sum = 0 and count = 0
					dataDict[hour] = (loc[0] + abs(round(pred[hour][symbol] - price, 2)), loc[1] + 1) # adds the price of the mapped value in the predicted dictionary to the sum and adds one to the count

			else:
				dataDict[hour] = None #if no entry exists for this hour in the predicted dictionary, the dataDict dictionary gets none input for the current hour

	fileHandler.close() #closes the file

	return(dataDict) # returns the created dictionary

# Finds the last hour that there is data for
# Inputs: sumDict - dictionary containing the hours as keys and tuples containing the sum and count as values
# Returns: last - integer representing the last hour that there is data for
def setLast(sumDict):
	# Checks that there is actually data in the dictionary
	if len(sumDict) < 1:
		raise DictError("No time periods detected. Check the actual.txt file for the proper format")

	last = list(sumDict)[-1] #captures the last hour

	# makes sure that the window size is not larger than the number of hours in the entire data set
	if last < windowNum:
		raise DictError("Window size is {}, which is larger than the number of timeperiods in actual.txt, which is {}.".format(windowNum, last))

	return(last)

# Initializes sumPrice and count values for the first window
# Inputs: windowNum - integer representing the window size
#         sumDict - dictionary containing the hours as keys and tuples containing the sum and count as values
# Returns: sumPrice - float representing the total sum of all the prices in all hours contained in the window 
#          count - integer representing the total number of values that were used to add up to the sum
def firstWindow(windowNum, sumDict):
	sumPrice = 0
	count = 0

	#for the entire window, gets the total sum and total count of all time periods in window
	for j in range(1, windowNum + 1):
		if sumDict.get(j) != None: #if there is no information for a hour nothing is added to sumPrice or count
			sumPrice+=sumDict[j][0]
			count+=sumDict[j][1]
	return(sumPrice, count) #returns the sumPrice and count values

# Calculates the sumPrice and count for the next window - doesn't recalculate unecessarily, simply subtracts the sum and count from the hour period falling out of the current time window and adds the sum and count of the hour that is entering the current time window 
# Inputs: sumPrice float representing the total sum of all the prices in all hours contained in the window 
#         count - integer representing the total number of values that were used to add up to the sum
#         sumDict - dictionary containing the hours as keys and tuples containing the sum and count as values
#         win_start - index of the hour where the window starts
#         win_end - index of the hour where the window ends
# Returns: sumPrice - float representing the total sum of all the prices in all hours contained in the window 
#          count - integer representing the total number of values that were used to add up to the sum
#          win_start - index of the hour where the window starts
#          win_end - index of the hour where the window ends
def slideWindow(sumPrice, count, sumDict, win_start, win_end):
	#increases the start and end locations of the window
	win_start+=1
	win_end+=1

	if sumDict.get(win_end) != None: # there is data for the time period entering the window
		if sumDict.get(win_start-1) != None: # there is data for the time period leaving the window
			sumPrice = sumPrice - sumDict[win_start-1][0] + sumDict[win_end][0] # subtracts the sum of the hour leaving the window, adds the sum of the hour entering the window
			count = count - sumDict[win_start-1][1] + sumDict[win_end][1] # subtracts the count of the hour leaving the window, adds the count of the hour entering the window
		else: # there is no data for the hour leaving the window
			sumPrice = sumPrice + sumDict[win_end][0] #adds the sum of the hour entering the window
			count = count + sumDict[win_end][1] # adds the count of the hour entering the window
	else: # there is no data for the hour entering the window
		if sumDict.get(win_start-1) != None: # there is data for the hour leaving the window
			sumPrice = sumPrice - sumDict[win_start-1][0] #subtracts the sum of the hour leaving the window
			count = count - sumDict[win_start-1][1] #subtacts the count of the hour leaving the window

	# returns the updated values
	return(sumPrice, count, win_start, win_end) 

# Calculates the average error for each winow and outputs the result to the comparison.txt file
# Inputs: sumDict - dictionary containing the hours as keys and tuples containing the sum and count as values
#         windowNum - integer representing the window size
#         comparisonFile - pointer to location in comparison.txt which is open and given write permissions
#         last - integer representing the last hour that there is data for
# Returns: None
def findAvgErr(sumDict, windowNum, comparisonFile, last):
	# starting values for the window
	win_start = 1
	win_end = windowNum

	# loop over every possible window in the data
	for i in range(1, last - windowNum + 2): 
		# if at the beginning, must build sumPrice and count with firstWindow()
		if i == 1:
			sumPrice, count = firstWindow(windowNum, sumDict)

		# if not at the beginning, use sliding window to update sumPrice and count values
		else:
			sumPrice, count, win_start, win_end = slideWindow(sumPrice, count, sumDict, win_start, win_end) 
			
		# if an entire window does not have any data, print win_start|win_end|NA
		if count == 0:
			comparisonFile.write("{}|{}|NA\n".format(win_start, win_end))

		# else print win_start|win_end|avgErr
		else:
			comparisonFile.write("{}|{}|".format(win_start, win_end)) 
			comparisonFile.write('{0:.2f}\n'.format(round(sumPrice/float(count), 2))) #formatting the output to always show 2 decimal places

# main function
if __name__ == '__main__':
	#reading input files - makes sure each file is correctly labeled in case files are not input in the same order every time
	actualFile, predictedFile, windowNum, comparisonFile = setFiles(sys.argv)

	# creates dictionary for predicted values
	predDict = setDict(predictedFile, {})

	# creates dictionary for use in calculating average error
	sumDict = setDict(actualFile, {}, True, predDict)

	# calculates the last hour that there is data for
	last = setLast(sumDict)

	#finds the average error and outputs the results to comparison.txt
	findAvgErr(sumDict, windowNum, comparisonFile, last)



	

























