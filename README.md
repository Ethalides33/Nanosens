# Nanosens
Tested on Python 3.11

Open the terminal (command prompt on Windows), and type the following:
`git clone https://github.com/Ethalides33/Nanosens.git`

Then, enter the newly created directory:<br/>
`cd Nanosens`

Now, create a python virtual environment. This step is not mandatory, but it is a good
habit to take. To create the virtual environment (venv), simply type:

`python.exe -m venv my_venv`

To activate the venv:<br/>
• On Linux: `source ./my_venv/bin/activate` <br/>
• On Windows: `(my_venv)$ \Scripts\activate.bat`<br/>

Finally, install the different dependencies required to run the simulation:<br/>
`(my_venv)$ pip install -r ./requirements.txt`<br/>

You should also create a _config.py_ file in the same directory in which you have the log-in ids formatted as a dict:
`config = {
  'user': 'username',
  'password': 'yourpassword',
  'host': 'DBIP',
  'database': 'DB name',
  'raise_on_warnings': True
}`

You can now run the software.<br/>
`(my_venv)$ python.exe .\main_admin_ui.py`<br/>

Once you are done, leave the virtual environment:<br/>
`(my_venv)$ deactivate`

## Data input
Important checklist:
- Make sure the article data is that of the original data source, _i.e._ do not use data referenced in an article using the latter article metadata.
- Verify that the papers studies 'normal' nanowire networks and not engineered structures based on such networks. Also avoid nanowire arrays.
- The standard for the transmittance values is to take it at 550 nm. If it is not done in the paper, verify it.
- In the DOI field, use the DOI and not the https:// adress associated to it.
- When taking data from Webplotdigitizer, use ; separators and reduce the number of decimals to maximum 3 (the total number of digits may vary depending on the number of non-decimal digits)
- In the first author field, use the full initials + full name of the author.
- Before commiting, check that the first and last values of the data correspond to the data on the graph (proofread before submitting...).
