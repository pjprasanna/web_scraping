#Importing libraries
import psycopg2
from selenium import webdriver
from configparser import ConfigParser
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

#Parser initializer
configur = ConfigParser()
configur.read('config.ini')

#DB connection
conn = psycopg2.connect(database ="postgres", user = "your_username",
						password = "your_password", host = "your_hostname",
						port = "port_number")

print("Connection Successful to PostgreSQL")
cur = conn.cursor() 


# Check if table exist
cur.execute("select * from information_schema.tables where table_name=%s", ('rto_details_selenium',))
if bool(cur.rowcount) == False:
       cur.execute(f"""
      CREATE TABLE rto_details_selenium
      (
      ID  SERIAL PRIMARY KEY,
      state_name TEXT NOT NULL,
      RTO_code TEXT NOT NULL,
      rto_name TEXT NOT NULL,
      Address TEXT NOT NULL,
      Phone_number TEXT,
      Office_timing TEXT
      )""")
       conn.commit()
       print("Table Created successfully")

#Chrome driver initialization
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options= chrome_options)
driver.maximize_window()

regional_name=[]
result=[]

driver.get('https://loconav.com/rto-offices/')

configur.add_section('state')


def statename_link():
      for i in range(1,8):
            for j in range(1,5):
                  textbox=driver.find_elements(By.XPATH,'/html/body/div[2]/div/div/div[5]/div/div[' +str(i) + ']/div[' +str(j) + ']/a')
                  for val in textbox:
                        configur.set('state',val.text,val.get_attribute('href'))

      with open("config.ini", 'w') as configfile:
              configur.write(configfile)

try:
       statename_link()
       print('State names are fetched...')
except:
       print('Failed to fetch state names...')
       driver.close()

def rto_details():
      for each_section in configur.sections():
             for (each_key, each_val) in configur.items(each_section):
                    s=each_val
                    driver.get(s)
                    row=driver.find_elements(By.CLASS_NAME,'state-offices-row')
                    for l in range(1,len(row)+1):
                                                regional_office=driver.find_elements(By.XPATH,'/html/body/div[2]/div/div/div[5]/div/div[' +str(l) + ']/a')
                                                for reg in regional_office:
                                                      driver.implicitly_wait(10)
                                                      regional_name.append(reg.text)
                                                      reg.click()
                                                      title=driver.find_elements(By.XPATH,'/html/body/div[2]/div/div/div[5]/div/h4')
                                                      for ti in title:
                                                            a=ti.text
                                                            #print(a)
                                                      for de in range(1,5):
                                                            que=driver.find_elements(By.XPATH,'/html/body/div[2]/div/div/div[5]/div/div/div[' +str(de) + ']/p[' +str(1) + ']')
                                                            ans=driver.find_elements(By.XPATH,'/html/body/div[2]/div/div/div[5]/div/div/div[' +str(de) + ']/p[' +str(2) + ']')
                                                            for q in que:
                                                                  for an in ans:
                                                                        #print(q.text," :",an.text)
                                                                        result.append(an.text) 
                                                      cur.execute(f"""INSERT INTO rto_details_selenium (state_name,RTO_code,rto_name,Address,Phone_number,Office_timing) VALUES ('{each_key}','{result[0]}','{a}','{result[1]}','{result[2]}','{result[3]}') """)
                                                      conn.commit()
                                                      result.clear()
                                                      driver.back()
      driver.back()

try:
        rto_details()
        print('RTO office details are stored...')
except:
        driver.close()
