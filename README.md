# Python Spreadsheet Automation

A small project to manage Automation in reporting procedure.


## Installation instructions

1. Clone the project. There will be GoogleSpreadSheetAutomation directory which has all the code.
2. I have used Ubuntu LTS 18.04 for testing things so If you can, Please use Linux/Debian based system
3. Python 3.X and pip3 versions must be installed to run the code. Better if you use latest version of python. Download instructions are [here](https://www.python.org/downloads/) 
4. You will need to create [Virtual Environment](https://docs.python.org/3/library/venv.html)

```
python3 -m venv env
```
If this shows you error like venv is not installed in system It will also show you command to install it. Use that command and again above command. 
After running it you will see a folder named env. 

5. Activate the virtual environment using this command
```
source env/bin/activate
```
6. Install packages from requirements.txt
```
pip install -r requirements.txt
```
7. Check if activated environment has all packages installed properly with,
```
pip freeze requirements.txt
```
**It should show these packages installed**
```
certifi==2019.9.11
chardet==3.0.4
Deprecated==1.2.7
gspread==3.1.0
httplib2==0.14.0
idna==2.8
numpy==1.17.4
oauth2client==4.1.3
pandas==0.25.3
pkg-resources==0.0.0
pyasn1==0.4.8
pyasn1-modules==0.2.7
python-dateutil==2.8.1
pytz==2019.3
requests==2.22.0
rsa==4.0
six==1.13.0
urllib3==1.25.7
wrapt==1.11.2
```

8. Program's execution is starting from `app.py` so running this code will start the script.
You must provide exactly 3 arguments,
   1. Report type
        - Appreciate
        - Smadex
        - The Trade Desk
        - DBM (Web)
        - DBM
    2. input directory path.
     3. output directory path.

```bash
python3 app.py --input "input" --output "output" --report_type "Appreciate"
```



**NOTE: Keep the quotes also as it is just change the values**


In real time, There is this method `start_everything` which takes these 3 arguments so you can directly pass it. Right now for testing use this command line arguments.

After the testing is done. You can add your own `Google Key Json` file and change the file name inside `report_config.json`. More on this file is down below.



### report_config.json

This file works as mapping file to get all the information. 

```
"google_credentials_file": "", # paste google json Credential File path here
  "spread_sheet": "", # paste Spreadsheet link here
  "reports": [
    {
      "report_type": "Appreciate",
      "spend_col": "spend",
      "campaign_col": "campaign_name",
      "daily_margin_column_name": "override_margin",
      "monthly_margin_column_name": "default_margin",
      "csv_date_format": "%d/%m/%Y"
    },
```

Above is the snapshot of file where,

1. `google_credentials_file` : Name of Key file of created GCP project.
2. `spread_sheet` : Link to the Google drive spreadsheet.
3. `reports` : List of reports where you can change the values for Local and Spreadsheet                     columns according to report.

    - `report_type` : One of the values from report types available.
    - `spend_col`: Name of the Spend column for any report
    - `campaign_col` : Name of campaign column
    - `daily_margin_column_name` : Column name in daily tab for any report
    - `monthly_margin_column_name` : Column name in monthly tab for any report
    - `csv_date_format`: The date format in the local CSV file. As we need the script to work with any date format.
      How can you defined different date formats? [Read here.](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)



**NOTE: Do not change the key of this JSON file, As in my code it's hard-coded access to these keys. Just change the values.**



After script is done running you should see output files inside the directory path you have provided for output. In our case with the command above it will be `output` 



## Additional info.

Library Used for fetching spreadsheets => [gspread](https://gspread.readthedocs.io/en/latest/)

### How to create GCP project and configure it with your spreadsheet?

Very well explained in starting of [this blog](https://towardsdatascience.com/accessing-google-spreadsheet-data-using-python-90a5bc214fd2)


*Some of the things worth mentioning*


- The file which is `spreadsheet` must be created with Google sheets. If you upload any `CSV` or `XLSX` file in Google sheet then it won't work. As, gspread will not be able to fetch that. Solution to this is for uploaded CSV/Excel you can create a copy and it will create a spreadsheet file.

