import mysql.connector
from mysql.connector import errorcode
from config import config
import datetime as date

gui_to_mysql_equiv = {'amd':'amd', 'Rs':'sheet_res', 'T':'trans', 'Haze':'haze', 'Emissivity':'emissivity', 'Lnw': 'nw_length', 'Dnw':'nw_diameter'}

def logToDB():
  try:
    cnx = mysql.connector.connect(**config)
    return cnx
  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      raise ConnectionError("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      raise ConnectionError("Database does not exist")
    else:
      raise ConnectionError("Impossible to connect to DB.")
  # else:
  #   cnx.close()

def sendData(conn, article_data, spectrum_data, values_data, x_data_header, y_data_header):
  article_key = article_data['first_author'] + article_data['year']
  spectrum_key = generate_spectrum_key(conn, article_key, x_data_header, y_data_header)
  print('key: ' + spectrum_key + '\n')
  log_article = send_article_data(conn, article_data, article_key)
  log_spectrum = send_spectrum_data(conn, spectrum_data, article_key, spectrum_key)
  log_values = send_values_data(conn, values_data, spectrum_key, x_data_header, y_data_header)
  return log_article, log_spectrum, log_values
  
def generate_spectrum_key(conn, article_key, x_data_header, y_data_header):
  temp_key = article_key + '_' + x_data_header.split(' ', 1)[0] + '_' + y_data_header.split(' ', 1)[0]
  if conn.is_connected:
      cursor = conn.cursor(buffered=True)
      try:
          cursor.execute('''SELECT * FROM spectra WHERE key_spectrum = (%s)''',(temp_key,))
          count = cursor.fetchone()
          while(count is not None):
              temp_key += '_I'
              cursor.execute('''SELECT * FROM spectra WHERE key_spectrum = (%s)''',(temp_key,))
              count = cursor.fetchone()
      except mysql.connector.Error as err:
          print("Error while sending data to DB: " + str(err))

  return temp_key

def send_spectrum_data(conn, spectrum_data, article_key, spectrum_key):
  spectrum_query = '''INSERT IGNORE INTO spectra (key_spectrum, article_key, material, coating, mean_d_nw, mean_l_nw, post_treatment, sim_data, comments, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
  print('sending spectrum data')
  spectrum_vals = (spectrum_key, article_key, spectrum_data['material'], spectrum_data['coating'], spectrum_data['nw_diameter'], spectrum_data['nw_length'], spectrum_data['post_treatment'], spectrum_data['sim_data'], spectrum_data['comments'], date.date.today())
  if conn.is_connected:
      cursor = conn.cursor(buffered=True)
      try:
              cursor.execute(spectrum_query, spectrum_vals) #Change values
              conn.commit()
              log_msg = f'Spectrum succesfully added to DB with key {spectrum_key}.'
              print(log_msg)
      except mysql.connector.Error as err:
          log_msg = "Error while sending data to DB: " + str(err)
  else:
    log_msg = "Error: not connected to DB..."
  return log_msg


def send_values_data(conn, values_data, spectrum_key, x_data_header, y_data_header):
  #WARNING: Table structure is hard coded in. If you change it, this function will not work anymore. You need to mirror the table changes to the code's ones.
   
  formatted_data = [] #'source', 'density', 'rsheet', 'trans', 'haze', 'value_comments' for each sublist; Modify this comment with table architecture to keep track
  columns = '(spectrum_key, ' + gui_to_mysql_equiv[x_data_header.split(' ', 1)[0]] + ', ' + gui_to_mysql_equiv[y_data_header.split(' ', 1)[0]] + ')'
  data_query = '''INSERT INTO data ''' + columns + ''' VALUES (%s, %s, %s)'''
  print(data_query)
  for r in values_data:
    temp_x = '{:.3f}'.format(float(r[0]))
    temp_y = '{:.3f}'.format(float(r[1]))
    formatted_data.append((spectrum_key, temp_x, temp_y))

  print(formatted_data)
  if conn.is_connected:
      cursor = conn.cursor(buffered=True)
      try:
          cursor.executemany(data_query, formatted_data) #Change values
          conn.commit()
          log_msg = 'Values succesfuly pushed to DB.'
          print(log_msg)
      except mysql.connector.Error as err:
          print(err)
          log_msg = "Error while sending values data to DB: " + str(err)
  else:
    log_msg = "Error: not connected to DB..."
  return log_msg

def send_article_data(conn, article_data, article_key):
  log_msg = ''
  article_query = '''INSERT IGNORE INTO articles (key_article, doi, first_author,publication_year,journal_abbr,comments, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
  
  article_vals = (article_key, article_data['doi'], article_data['first_author'], article_data['year'], article_data['journal'], article_data['comments'], date.date.today())
  if conn.is_connected:
      cursor = conn.cursor(buffered=True)
      try:
          cursor.execute('''SELECT * FROM articles WHERE key_article = (%s)''',(article_key,))
          count = cursor.fetchone()
          if(count is not None):
              log_msg = f'Article with key {article_key} already exists in database ! Skipping article data insert, pushing values to associated key.'
              print(log_msg)
          else:
              cursor.execute(article_query, article_vals) #Change values
              conn.commit()
              log_msg = f'Article succesfully added to DB with key {article_key}.'
              print(log_msg)

      except mysql.connector.Error as err:
          log_msg = "Error while sending data to DB: " + str(err)
  else:
    log_msg = "Error: not connected to DB..."
  return log_msg
