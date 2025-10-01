
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
        folderPath = './storage/'+time
        with open(folderPath,'w') as node_file:
            node_file.write(operation)
            node_file.write('\n')
            if (operation == 'update'):
                node_file.write(old_data)
                node_file.write('\n')

            node_file.write(new_data)
            node_file.write('\n')
            node_file.write('hash: ')
            node_file.write(hash)



    def hash_function(self):
        return '1'
        



if __name__ == '__main__':
    struc = PatientRecord()
    struc.add_node('update','test old data','test new data')
