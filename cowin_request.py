import requests
import datetime
import json
import sqlite3
import pandas as pd
from datetime import datetime as dt
import copy

'''importing the analysis class from analysis.py in order to analyse the obtained data'''
import analysis 

'''
createDatabase() is just a helper function which optimises the data for appropriate parameters
 and creates the resultant database in SQLite
'''
def createDatabase ( sessions ):

    conn = sqlite3.connect ( 'CoWIN.db' )
    c = conn.cursor ()

    for session in sessions:
        session.pop('block_name')
        session.pop('date')
        session.pop('district_name')
        del session['from']
        del session['pincode']
        del session['session_id']
        del session['to']
        del session['slots']

    df = pd.DataFrame.from_dict(sessions)
    df.to_sql('sessions', conn, if_exists = 'replace', index = False)
    c.close()

class track:

    def __init__(self, trackPincode:int, trackDistrict:str, state: str, age: int, dose: int):

        self.pincode = trackPincode
        self.district = trackDistrict
        self.state = state
        self.date = datetime.date.today().strftime("%d-%m-%Y")
        self.age = age
        self.available = []

        if dose == 1:
            self.dose = 'available_capacity_dose1'
        elif dose == 2:
            self.dose = 'available_capacity_dose2'
        self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2866.71 Safari/537.36'}


    '''CoWin is pretty whack so search by pincode doesn't give consistent results'''
    def getByPin(self):
        apiEndPoint = \
            'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode={}&date={}'.format(self.pincode, self.date)
        response = requests.get(apiEndPoint, headers = self.headers)
        data = response.json()
        print(data)


    '''So I'm gonna use the other method which involves:
        1) get all the states to find the stateID of concerned state
        2) use stateID to get districtID of concerned district
        3) use districtID and get relevant data (finally) 
    '''
    def getStateID(self):
        apiEndpoint = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'
        response = requests.get(apiEndpoint, headers = self.headers)
        states = response.json()

        for state in states['states']:
            if state['state_name']==self.state:
                self.getDistrictID(state['state_id'])

    def getDistrictID(self, stateId:int):
        apiEndpoint = 'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}'.format(stateId)
        response = requests.get(apiEndpoint, headers = self.headers)
        districts = response.json()

        for district in districts['districts']:
            if district['district_name'] == self.district:
                self.getVaccine(district['district_id'])

    def getVaccine(self, districtId):
        apiEndpoint = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={}&date={}'.format(districtId, self.date)
        response = requests.get(apiEndpoint, headers = self.headers)
        data = response.json()
        self.sessions = data['sessions']
        createDatabase(self.sessions)       # Creating a SQL database to store this result

    '''
    For now I'm going to write down a log of the vaccine slots available for given parameters and 
    using crontab make a system automation which runs this script ever minute to get data back
    '''
    def notify(self):
        self.getStateID()
        conn = sqlite3.connect('CoWIN.db')
        c = conn.cursor()

        getVaccineForAge = ''' SELECT name, address, vaccine, min_age_limit, lat, long FROM sessions WHERE NOT {}=0 '''.format(self.dose)
        c.execute(getVaccineForAge)
        self.available = c.fetchall()

        with open('Vaccine_log.txt', 'a', encoding = 'utf-8') as f:
            f.write('\n')
            now = dt.now()
            dt_string = now.strftime ( "%d/%m/%Y %H:%M:%S" )
            f.write(dt_string)
            f.write('\n')
            for i in self.available:
                f.write(str(i))
                f.write('\n')
        f.close()

if __name__ == '__main__':

    me = track(400098, 'Mumbai', 'Maharashtra', 18, 1)
    me.notify()
    output = analysis.analysis(me.available)

