import urllib3
import psycopg2
from bs4 import BeautifulSoup
from requests import get
urllib3.disable_warnings()

#DB connection
conn = psycopg2.connect(database ="postgres", user = "your_username" password = "your_passwd", host = "your_hostname",port = "port_number")
print("Connection Successful to PostgreSQL")
cur = conn.cursor() 

# Check if table exist
cur.execute("select * from information_schema.tables where table_name=%s", ('rto_details_request',))
if bool(cur.rowcount) == False:
       cur.execute(f"""
      CREATE TABLE rto_details_request
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
       print("Table Created successfully...")


def rto_details(state_page,state):
    for row in state_page.find(class_="state-offices").find_all(class_="state-offices-row"):
        rto_name_and_code=row.find_all('p')
        rto_name=rto_name_and_code[0].text
        rto_link=row.find('a')['href']
        rto_link="https://loconav.com"+rto_link
        try:
            response=get(rto_link,verify=False)
            response.raise_for_status()
            each_key=state[13:]
            a=rto_name
            detail = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error occurred while retrieving RTO details: {e}")
        rto_card_det=[]
        for rto_det_row in detail.find(class_="card-details").find_all(class_="card-details-row"):
            rto_card_det.append(rto_det_row.find_all('p')[1].text)
        #print('RTO code :',rto_card_det[0],'\nRTO address :',rto_card_det[1],'\nRTO phone number :',rto_card_det[2],'\nRTO timing :',rto_card_det[3],'\n')
        cur.execute(f"""INSERT INTO rto_details_request (state_name,RTO_code,rto_name,Address,Phone_number,Office_timing) VALUES ('{each_key}','{rto_card_det[0]}','{a}','{rto_card_det[1]}','{rto_card_det[2]}','{rto_card_det[3]}') """)
        conn.commit()
    print("\nRTO details stored for",each_key,"...")
    
def all_states():
    response=get('https://loconav.com/rto-offices',verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    state_list=[]
    state_link=[]
    for link in soup.find(class_="clearfix statewise-rto").find_all('a'):
        state_list.append(link.text)
        state_link.append(link['href'])
    for state in state_link:
        #print("\nState name :",state[13:].upper(),'\n')
        response2=get(f'https://loconav.com/{state}',verify=False)
        state_page = BeautifulSoup(response2.text, 'html.parser')
        rto_details(state_page,state)

all_states()
