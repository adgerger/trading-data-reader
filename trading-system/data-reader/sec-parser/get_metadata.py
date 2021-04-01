import os

#dir_list = os.listdir('test/')
#print("Len is "+ str(len(dir_list)))

years = ['2020','2019','2018','2017','2016','2015','2014','2013','2012',
'2011','2010','2009','2008','2007']


fp = open("../../../data/tickers.txt", "r")
fout = open("../../../data/metadata.txt", "w+")
ferr = open("../../../data/errortickers.txt", "w+")

lines = fp.readlines()

for ticker in lines:
    ticker = ticker.strip("\n")
    desc = "***** TICKER "+ ticker + " *****\n"

    log =  "***** TICKER "+ ticker + " *****\n"

    for year in years:
        dir_path = "../../../data/" + ticker + "/" + year + "/unprocessed/"

        if os.path.exists(dir_path):
            file_count = len(os.listdir(dir_path))
            if file_count != 4:
                desc = desc + "YEAR " + year + " HAS " + str(file_count) + " FILES.\n"

            if file_count > 4:
                log = log + "YEAR " + year + " HAS " + str(file_count) + " FILES.\n"


    desc = desc + "*" * (19 + len(ticker))
    desc = desc + "\n\n"
    if log != "***** TICKER "+ ticker + " *****\n":
        log = log + "*" * (19 + len(ticker))
        log = log + "\n\n"
        ferr.write(log)


    fout.write(desc)

    log = ""
    desc = ""

fp.close()
fout.close()
ferr.close()


