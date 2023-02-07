# Nanosens

Open the terminal (command prompt on Windows), and type the following:
`git clone https://github.com/Ethalides33/Nanosens.git`

Then, enter the newly created directory:
cd Nanosens

Now, create a python virtual environment. This step is not mandatory, but it is a good
habit to take. To create the virtual environment (venv), simply type:

`python3 -m venv my_venv`
To activate the venv:
• On Linux: `source ./my venv/bin/activate`
• On Windows: `(myvenv)$ \Scripts\activate.bat`

Finally, install the different dependencies required to run the simulation:
`(my_venv)$ pip install -r ./requirements.txt`
You can now run the software. Simply type:
`(my_venv)$ python.exe .\main_admin_ui.py`
Once you are done, leave the virtual environment:
`(my_venv)$ deactivate`


