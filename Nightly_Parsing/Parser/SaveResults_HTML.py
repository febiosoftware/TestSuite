import datetime
def SaveFinalResultsHTML (Results):
	#Create a file for outputting the data
	today = datetime.date.today()
	#used to be "../Resources/"
	filepath = '../Nightly_Runs/' 
	HTMLFile = '../Nightly_Results/nightly_results-' + str(today) + '.html'
	with open(HTMLFile, "w") as output:
		#Print the HTML header *** Note the write function will include
		#all white spaces
		output.write("""
		<html>
		<head>
		<title>Testing Results</title>
		<style type="text/css">
		#Fixed{width:80px}
		</style>
		</head>
		<body>""")
                 
        ##### First Table #####         
        #Create the table with two columns and a row for each machine
        #List the number of files each machine tested.
		output.write("""
		<!--Table 1: Compares # files tested for each machine-->
		<table border="1">
		<tr>
		<th colspan="2"> Files Tested </th>
		</tr>
		<tr>
		<td> Machine </td> <td> # Files </td>
		</tr>""")
		for file in Results._files:
			machine = file.replace(filepath,"")
			machine = machine.replace(".txt","")
			num_files = str(Results._current_Output[file]['Numb Files'])
			row = "<tr><td>" + machine + "</td><td>" + num_files + "</td></tr>"
			output.write(row)
		output.write("</table>")
        
        ##### Second Table #####
        #Make a table used to display any errors reported with the 
        #standard files used.
		output.write("""
        <br>
        <!--Table 2: Standard Files Errors-->
        <table border="1">
        <tr>
        <th colspan="10"> Standard Files Errors </th>
        </tr>""")
		
		for file in Results._files:
			machine = file.replace(filepath, "")
			machine = machine.replace(".txt", "")
			for key in Results._standard_Errors[file].keys():
				id_tag = "<tr><td>" + machine + " - " + key + "</td>"
				output.write(id_tag)
				for col in range (len(Results._standard_Errors[file][key])):
					col_tag = "<td>" + Results._standard_Errors[file][key][col] + "</td>"
					output.write(col_tag)
				output.write("</tr>")    
				
		output.write("</table>")
        
        ##### Third Table #####
        #### Standard Files Missing ####
		output.write("""
        <br>
        <!--Table 3: Missing Standard Files-->
        <table border="1">
        <tr>
        <th colspan="2"> Missing Standard Files </th>
        </tr>""")
		
		for file in Results._files:
			machine = file.replace(filepath, "")
			machine = machine.replace(".txt", "")
			for key in Results._standard_Missing[file]:
				row = "<tr><td>" + machine + "</td><td>" + key + "</td></td>"
				output.write(row)
				
		output.write("</table>")
        
        ##### Fourth Table #####
        #### Output the Error terminations #### 
		output.write("""
        <br>
        <!--Table 4: Error Terminations-->
        <table border="1">
        <tr>
        <th colspan="7"> Error Terminations </th>
        </tr>""")
    
            
        #Write the Machine names across the top
		output.write("<tr><td></td>")
		for file in Results._files:
			machine = file.replace(filepath, "")
			machine = machine.replace(".txt", "")
			col = "<td>" + machine + "</td>"
			output.write(col)
		output.write("</tr>")
        
        #Loop through the files and output errors
		for key in Results._current_Errors.keys():
			row_tag = "<tr><td>" + key + "</td>"
			output.write(row_tag)
			for col in range (len(Results._current_Errors[key])):
				col = "<td>" + Results._current_Errors[key][col] + "</td>"
				output.write(col)
			output.write("</tr>")
		output.write("</table>")
        
        ##### Fifth Table #####
        #### Write out the Variations 
		output.write("""
        <br>
        <!--Table 5: Variations-->
        <table border="1">
        <tr>
        <th colspan="10"> Variations </th>
        </tr>
        <tr>
        <td colspan="2"> - = Nothing Wrong </td>
        <td colspan="2"> M = Missing Standard </td>
        <td colspan="2"> R = Residual </td>
        <td colspan="2"> S = Steps </td>
        <td colspan="2"> U = Unknown Issue </td>
        </tr>""")
        
        #Write the Machine names across the top
		output.write("""
        <tr><td id=""Fixed""></td><td id=""Fixed""></td>"
        <td id=""Fixed""></td><td id=""Fixed""></td>""")
		for file in Results._files:
			machine = file.replace(filepath, "")
			machine = machine.replace(".txt", "")
			col = "<td id=""Fixed"">" + machine + "</td>"
			output.write(col)
		output.write("</tr>")
		
		for key in Results._variations.keys():
			row_id = "<tr><td colspan=""4"">" + key + "</td>"
			output.write(row_id)
			for col in range (len(Results._variations[key])):
				temp = "<td>" + Results._variations[key][col] + "</td>"
				output.write(temp)
			output.write("</tr>")
		output.write("</table>")
        
        #Close off the HTML File
		output.write("</body></html>")
	output.close()  