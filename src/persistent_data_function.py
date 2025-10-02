import platform
import stat
import os
from datetime import datetime

class PatientRecord:
    def __init__(self):
        self.tree = None



    def getCurrentTime(self):

        # Get current time
        now = datetime.now()

        # Format as DD-MM-YYYY HH:MM:SS (24-hour)
        formatted_time = now.strftime("%d-%m-%Y %H:%M:%S")
        formatted_time = formatted_time.replace(':','-')
        return formatted_time


        

    def add_node(self,operation, old_data,new_data):
        time = self.getCurrentTime()
        hash = self.hash_function()
        filePath = './storage/'+time
        with open(filePath,'w') as node_file:
            node_file.write(operation)
            node_file.write('\n')
            if (operation == 'update'):
                node_file.write(old_data)
                node_file.write('\n')

            node_file.write(new_data)
            node_file.write('\n')

            node_file.write('hash: ')
            node_file.write(hash)


        platform_type = platform.system()
        if (platform_type == 'Windows'):
            os.chmod(filePath,stat.S_IREAD)
        else:
            os.chmod(filePath,0o444)

        print(f"Added node with name {filePath} and \nmade it readonly on platform: {platform_type}")



    def convert_patient_data_to_str(self,data):
        if (len(data) != 4):
            print("Invalid data has been given to the converting patient data to str function")
            return None

        id = data[0]
        name = data[1]
        isCured = data[2]
        diseases = data[3]
        res = f"{str(id)} {name} {str(isCured)} ["
        for i in range(len(diseases)):
            if (i != len(diseases)-1):
                res+= f"{diseases[i]},"
            else:
                res+= f"{diseases[i]}"

        res+="]"

        return res

            





    def hash_function(self):
        return '1'
        



if __name__ == '__main__':
    struc = PatientRecord()
    struc.add_node('update','test old data','test new data')
