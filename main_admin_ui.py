import sys
import webbrowser
import qdarktheme as dtheme
import numpy as np
from math import sin, tan, radians

import db_connection as db

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QScrollArea, QTableWidgetItem
)
#from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5 import QtGui

from admin_ui import Ui_MainWindow

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setAcceptDrops(True)
        self.db_conn = self.db_connection()
        self.init_pyqt_connections()
        self.data_table.installEventFilter(self)

    def db_connection(self):
        try:
            cnx = db.logToDB()
            self.Log(f'Connected to database. MySQL server version on {cnx.get_server_info()}. \n')
            return cnx
        except ConnectionError as err:
            self.Log(err)
            return

    def manual_db_connection(self):
        if(self.db_conn.is_connected()):
            self.Log("Already connected to database.")
            return
        else:
            self.db_conn=self.db_connection()
            return

    def disconnect_db(self):
        if(self.db_conn.is_connected()):
            self.db_conn.close()
            self.Log("Disconnected from DB.")
            return
        else:
            self.Log("Not connected to DB.")
            return
    
    def show_db_status(self):
        if(self.db_conn.is_connected()):
            self.Log('Currently connected to DB. MySQL version '+ self.db_conn.get_server_info() + '.')
        else:
            self.Log('Currently disconnected from DB.')

    def open_Documentation(self):
        webbrowser.open_new('https://www.google.com')

    def open_contact(self):
        webbrowser.open_new('https://www.spin.uliege.be/cms/c_7014551/en/spin-team')
    
    def init_pyqt_connections(self):
        self.actionConnect_to_DB.triggered.connect(self.manual_db_connection)
        self.actionDisconnect_from_DB.triggered.connect(self.disconnect_db)
        self.actionDB_status.triggered.connect(self.show_db_status)
        self.actionDocumentation.triggered.connect(self.open_Documentation)
        self.actionContact_us.triggered.connect(self.open_contact)

        self.x_data_box.currentTextChanged.connect(self.rename_x_column)
        self.y_data_box.currentTextChanged.connect(self.rename_y_column)

        self.reset_article_data_button.clicked.connect(self.reset_article_data)
        self.reset_spectrum_metadata_button.clicked.connect(self.reset_spectrum_metadata)
        self.reset_spectrum_data_button.clicked.connect(self.reset_spectrum_data)
        self.commit_data_button.clicked.connect(self.send_data)

        self.apply_button.clicked.connect(self.apply_transformation)


    def rename_x_column(self):
        self.Log("Changed x axis data to " + self.x_data_box.currentText())
        self.data_table.horizontalHeaderItem(0).setText(self.x_data_box.currentText())

    def rename_y_column(self):
        self.Log("Changed y axis data to " + self.y_data_box.currentText())
        self.data_table.horizontalHeaderItem(1).setText(self.y_data_box.currentText())
            
    def reset_article_data(self):
        self.doi_text.setText("")
        self.first_author_text.setText("")
        self.pub_year_text.setText("")
        self.journal_text.setText("")
        self.article_comments_text.setText("")

        self.Log("Article data reset succesfuly.")

    def reset_spectrum_metadata(self):
        print("test")
        self.material_box.setCurrentIndex(0)
        self.coating_box.setCurrentIndex(0)
        self.nw_length_text.setText("")
        self.nw_diameter_text.setText("")
        self.post_treatment_box.setCurrentIndex(0)
        self.sim_checkbox.setChecked(False)
        self.spectrum_comments_text.setText("")

        self.Log("Spectrum  metadata reset succesfuly.")

    def reset_spectrum_data(self):
        for r in range(self.data_table.rowCount()):
            for c in range(self.data_table.columnCount()):
                if(self.data_table.item(r,c) is not None): #Should check if int or str depending on column.
                    self.data_table.setItem(r, c, QTableWidgetItem(""))

        self.Log("Spectrum  data reset succesfuly.")

    def Log(self,message):
        self.logs_text.append(message)


    def send_data(self):
        self.Log("Sending data. Please wait...") #need to make asynchroneous or qthreads or sth if timing becomes a problem
        
        article_data = self.retrieve_article_data() #dict
        if not article_data: #Si manque données alors 'retrieve_article_data' renvoie False
            return
        print(article_data)
        spectrum_data = self.retrieve_spectrum_data()
        if not spectrum_data:
            return
        print(spectrum_data)
        check, values_data = self.retrieve_values_data() #list of lists
        print(values_data)
        if(check):
            send_status = db.sendData(self.db_conn, article_data, spectrum_data, values_data, self.data_table.horizontalHeaderItem(0).text(), self.data_table.horizontalHeaderItem(1).text())
            for s in send_status:
                self.Log(s)
            #self.Log(send_status + '\n') #This is a terrible way of doing this but I'm too bored to do it right or to even assign the result to a temp var oops
        #self.Log("Data sent succesfully.") #should log summary of sent data
    
    def retrieve_article_data(self):
        if(not self.doi_text.text() or not self.first_author_text.text() or not self.pub_year_text.text()):
            self.Log('DOI, first author and publication year must be filled.')
            return False
        if not self.pub_year_text.text().isdigit():
            self.Log('Publication year must be of type integer.')
            return False

        article_data = {'doi':self.doi_text.text(), 'first_author':self.first_author_text.text(), 'year':self.pub_year_text.text(), 'journal': self.journal_text.text(), 'comments':self.article_comments_text.toPlainText()}
        return article_data

    def retrieve_spectrum_data(self):

        if self.nw_length_text.text():
            try:
                float(self.nw_length_text.text())
            except ValueError:
                self.Log('NW length must be of type float.')
                return False

        if self.nw_diameter_text.text():
            try:
                float(self.nw_diameter_text.text())
            except ValueError:
                self.Log('NW diameter must be of type float.')
                return False

        spectrum_data = {'material': self.material_box.currentText(), 'coating':self.coating_box.currentText(), 'nw_length':self.nw_length_text.text(), 'nw_diameter':self.nw_diameter_text.text(), 'post_treatment':self.post_treatment_box.currentText(), 'sim_data':str(int(self.sim_checkbox.isChecked())), 'comments':self.spectrum_comments_text.toPlainText()}
        
        if not spectrum_data['nw_length']:
            spectrum_data['nw_length'] = None
        if not spectrum_data['nw_diameter']:
            spectrum_data['nw_diameter'] = None
        return spectrum_data

    def retrieve_values_data(self):
        data_values = []
        for r in range(self.data_table.rowCount()):
            data_values.append([])
            for c in range(self.data_table.columnCount()):
                if(self.data_table.item(r,c) is not None): #Should check if int or str depending on column.
                    data_values[r].append(self.data_table.item(r,c).text())
                else:
                    data_values[r].append(None) # None means no value.

        filtered_data = [lst for lst in data_values if any(lst)] #Removing empty rows
        check = True
        for lst in filtered_data:
            for val in lst: #last element is comment so str
                if val is not None:
                    try:
                        float(val)
                    except ValueError:
                        self.Log('Inserted values must all be floating numbers. Please verify your input table.')
                        check = False
        self.reset_spectrum_data() #○delete data after commit
        return check, filtered_data


    def apply_transformation(self):
        # Custom factor has priority over toolbox.
        column_index = 0 if str(self.apply_toolbox.currentText()) == 'X column' else 1

        if self.customfactor_text.text():
            self.apply_custom_factor(column_index, str(self.customfactor_text.text()))
            return
        else:
            choice = str(self.transformation_toolbox.currentText())
            if choice == 'X100':
                self.apply_custom_factor(column_index, '100')
                return
            elif choice == '#/m^2->mg/m^2':
                if self.nw_diameter_text.text() is None or self.nw_length_text.text() is None:
                    self.Log('Mean diameter and lenth of the nanowires are required to perform this transformation ! Cancelling operation.')
                    return
                try:
                    diameter = float(str(self.nw_diameter_text.text()))
                    length = float(str(self.nw_length_text.text()))
                except:
                    self.Log('Diameter and length of diameter must be of type float!')
                    return

                factor = str(1.049*10**(-8) * length * (5*(diameter*10**(-3))**2)/(16*sin(radians(54))**2*tan(radians(36)))) #all in micrometers, returns mg
                self.apply_custom_factor(column_index, factor)
                return
            elif choice == '/cm^2-> /m^2':
                self.apply_custom_factor(column_index, '10000')
                return
            elif choice == '/mm^2 -> /m^2':
                self.apply_custom_factor(column_index, '1000000')
                return
            elif choice == 'Cond to res':
                self.inverse_data(column_index)
                return
            return
        

    def apply_custom_factor(self, column_index, factor):
        try:
            factor = float(factor)
        except:
            self.Log('Factor must be of type float ! Cancelling operation.')
            return

        for r in range(self.data_table.rowCount()):
            if(self.data_table.item(r,column_index) is not None): #Should check if int or str depending on column.
                try:
                    float(str(self.data_table.item(r,column_index).text()))
                except:
                    self.Log('Data must all be of type float ! Cancelling operation.')
                    return
                self.data_table.setItem(r, column_index, QTableWidgetItem(str(factor*float(str(self.data_table.item(r,column_index).text())))))
        self.Log('Applied custom factor to column ' + str(self.apply_toolbox.currentText()))
        return

    def inverse_data(self, column_index):
        for r in range(self.data_table.rowCount()):
            if(self.data_table.item(r,column_index) is not None): #Should check if int or str depending on column.
                try:
                    float(str(self.data_table.item(r,column_index).text()))
                except:
                    self.Log('Data must all be of type float ! Cancelling operation.')
                    return
                if float(str(self.data_table.item(r,column_index).text())) == 0:
                    self.Log('Cannot divide by zero. Cancelling operation.')
                    return
                self.data_table.setItem(r, column_index, QTableWidgetItem(str(1/float(str(self.data_table.item(r,column_index).text())))))
        
        self.Log('Inverted data for column ' + str(self.apply_toolbox.currentText()))
        return

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        conv = lambda el: float(el.replace(b',',b'.'))

        all_files = [u.toLocalFile() for u in event.mimeData().urls()]
        filtered_files = [f for f in all_files if f.endswith(".csv")]
        if (len(filtered_files)==1):
            csv_data = np.genfromtxt(filtered_files[0], delimiter=';', converters={i:conv for i in range(2)}) #conv to go from , decimal to .
            csv_data_str = np.array(["%.3f" % x for x in csv_data.reshape(csv_data.size)]) #str formatting
            csv_data_str = csv_data_str.reshape(csv_data.shape)            

            for rownbr, rowdata in enumerate(csv_data_str):
                item_x = QTableWidgetItem(rowdata[0])
                item_y = QTableWidgetItem(rowdata[1])

                self.data_table.setItem(rownbr, 0, item_x)
                self.data_table.setItem(rownbr, 1, item_y)
        elif(len(filtered_files)>1):
            self.Log('More then one data file was recieved. Please make sure only one file is provided per spectrum.')
        else:
            self.Log('File must be of type csv !')

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and event.matches(QtGui.QKeySequence.Paste)):
            # ensure that the table receives the key event first
            res = super().eventFilter(source, event)
            
            to_paste = QApplication.clipboard().text().split('\n')[:-1] #the [:-1] omits the last character aka \n
            if len(to_paste) == 0:
                return False
            to_paste_rows = [row.split(';') for row in to_paste]
            for i, row in enumerate(to_paste_rows):
                if i>50:
                    break
                item1 = QTableWidgetItem(str(row[0]).replace(',','.'))
                item2 = QTableWidgetItem(str(row[1]).replace(',','.'))
                self.data_table.setItem(i, 0, item1)
                self.data_table.setItem(i, 1, item2)
            self.Log('Data pasted succesfully.')                
            return res
            self.Log('There was a problem pasting data. Please ensure the datatypes are floats.')
        return super().eventFilter(source, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dtheme.setup_theme()
    win = Window()
    win.showMaximized()
    sys.exit(app.exec())()