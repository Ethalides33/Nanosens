# Nanosens

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

You can now run the software.<br/>
`(my_venv)$ python.exe .\main_admin_ui.py`<br/>

Once you are done, leave the virtual environment:<br/>
`(my_venv)$ deactivate`


