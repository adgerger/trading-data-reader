
--------
Overview
--------

The goal of this program is to get financial statements directly from the SEC and process and normalize it to be used in analysis, it only supports the years for which 
SEC has interactive XBRL data for a company, which usually goes back 10 years.


------------
How it works
------------

This program, for a given ticker or a list of tickers, finds the CIK numbers for the given tickers, access an SEC endpoint where it lists all the 10K or 10Q filings,
finds all the supported years and grabs the filing names for each filing for the supported years, then it access the index for that given filing and downloads the xlsx
file that contains the financial statements, then it reads the xlsx file and processes it, and writes it back into csv files or returns it as a dataframe, making it 
ready to use. 


