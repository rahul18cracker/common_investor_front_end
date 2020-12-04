# pre-pop-company-db.py
# This file will help pre populate the CommonStock DB which contains the name of all companies in S&P 500
# Once this DB is populated it will help search a company from the search page to make sure a valid
# ticker symbol/Company is searched for
import csv
import os
from base.models import CommonStock


# Mechanism or steps
# 1. Read the CSV file, this is a static file for now but will be made to pull from S3 bucket later Issue:#2
# 2. After the file is read get the 3 values out and store to the DB CommonStock
# 3. Remeber this is astandalone script for setup only if the DB is empty

def run() -> 'None':
    """
    Function will read the CSV file and pre-populate the DB. This DB will be used to run the user seraches
    for a company name(e.g. 'Apple Computers') or company ticker symbol(e.g. 'aapl')
    :return: None
    :rtype: None
    """
    with open(os.getcwd() + '/scripts/constituents_csv.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        # Run past the first row as it's the header
        next(csv_reader)
        # Clear all the initial entries
        print(f"Deleted {CommonStock.objects.all().delete()} objects")
        for count,row in enumerate(csv_reader):
            print(f"Processing symbol:{row[0]} | Name:{row[1]} | Sector:{row[2]} row: {count}")
            # Save the data to the DB, rememeber the form_type is set to default 10-k in models
            # that is why only CSV read fields are saved here
            # Table 'commonstock' will look like
            # index | ticker symbol | Name            | Sector                 | form_type
            # 9665 | YUM            | Yum! Brands Inc | Consumer Discretionary | 10-k
            # Hint: commands to see in dbshell
            # python manage.py dbshell >> Start the shell
            # SELECT * FROM commonstock;  >> Display all the values in commonstock table
            CommonStock(symbol=row[0],
                        Name=row[1],
                        Sector=row[2]).save()




