# Alex Grieco prediction-validation.py

My approach was as follows:

First, I parse the arguments and assign variables to the correct input file. I have made the decision to not assume that the files are input in the same order every time and allow for the user to change the order of the input files to give them more flexibility. 

Next, I parsed the predicted.txt file and created a multilayered dictionary with hour as the key to the outermost level, and then stock symbol the key to the inner level with price as the value. Thus hour would be a key to a list of symbol:price key value pairs.

Next, I parsed the actual.txt file and created a dictionary (sumDict) with hour as the key and the value a tuple of (sum, count) where sum is the sum of all the calculated differences between the prices in actual.txt and predicted.txt and count is the number of values that were used to calculate that sum (i.e. this would be used in the average error calculation later). 

I then determined the last hour that there is data for so that I knew how many iterations to do.

Using the iterations I then looped over the entire length of sumDict minus the window size to calculate the average error for each window. To start, I summed up every (sum, count) tuple in the first window. Then after that, I would subtract the values from the hour that is falling out of the window and add the values from the hour that is entering the new window. In this way, I avoid recalculating the same values over and over again, especially for large window sizes. I traverse the entire length of sumDict once. At each iteration, I output the respective contents to the comparison.txt file.





