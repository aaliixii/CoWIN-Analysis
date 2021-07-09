import copy 
import icecream as ic
import pandas as pd
from datetime import datetime as dt
import os


def optimiseList(test):
    tempList = []
    now = dt.now()
    dt_string = now.strftime ( "%d/%m/%Y %H:%M:%S" )

    for i in test:
        temp = list(i)
        temp.insert(0,dt_string)
        tempList.append(temp)
    return tempList


class analysis:

    def __init__(self, available):

        self.data = available
        self.appendToExcel()

    def appendToExcel(self):
        
        file = "COWIN_data.xlsx"
        dfList = optimiseList(copy.deepcopy(self.data))
        
        df = pd.DataFrame(dfList, columns=['Date & Time','Centre','Address','Vaccine','Age', 'Lat', 'Long'])
        
        # First checking if the Excel file already exists; if exists then save and break
        if not os.path.isfile(file):
            with pd.ExcelWriter(file, engine = 'xlsxwriter') as writer:
                df.to_excel(writer, sheet_name = 'Data')
            return

        writer = pd.ExcelWriter(file, engine = 'openpyxl', mode = 'a')
        print(writer.sheets)
        startRow = writer.book['Data'].max_row
        writer.sheets = {ws.title:ws for ws in writer.book.worksheets}

        df.to_excel(writer, sheet_name='Data', startrow=startRow, header=None)
        writer.save()
    
    def timeAnalysis(self,*args):
        pass

    def geoAnalysis(self,*args):
        pass
