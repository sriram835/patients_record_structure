import platform
import stat
import os
from datetime import datetime

class PatientRecord:
    def __init__(self):
        self.tree = None
        self.storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
        os.makedirs(self.storage_dir, exist_ok=True)



    def getCurrentTime(self):

        # Get current time
        now = datetime.now()

        # Format as DD-MM-YYYY HH:MM:SS (24-hour)
        formatted_time = now.strftime("%d-%m-%Y %H:%M:%S")
        formatted_time = formatted_time.replace(':','-')
        return formatted_time


        

    def add_node(self,operation, old_data,new_data):
        timestamp = self.getCurrentTime()
        hash = self.hash_function()
        filePath = os.path.join(self.storage_dir,timestamp) 

        with open(filePath,'w') as node_file:
            node_file.write(operation)
            node_file.write('\n')
            if (operation == 'update'):
                old_data_str = self.convert_patient_data_to_str(old_data)
                if (old_data_str is None):
                    return False
                node_file.write(old_data_str)
                node_file.write('\n')

            new_data_str = self.convert_patient_data_to_str(new_data)
            if (new_data_str is None):
                return False
            node_file.write(new_data_str)
            node_file.write('\n')

            node_file.write('hash: ')
            node_file.write(hash)


        platform_type = platform.system()
        if (platform_type == 'Windows'):
            os.chmod(filePath,stat.S_IREAD)
        else:
            os.chmod(filePath,0o444)

        print(f"Added node with name {filePath} and \nmade it readonly on platform: {platform_type}")
        return True



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


    
    def sort_file_names(self, files):
        if not files:
            return []

        def partition(low, high):
            pivot = files[(low + high) // 2]
            i, j = low, high
            while i <= j:
                while self.isNewerThanFirstFile(files[i], pivot):  # files[i] < pivot
                    i += 1
                while self.isNewerThanFirstFile(pivot, files[j]):  # files[j] > pivot
                    j -= 1
                if i <= j:
                    files[i], files[j] = files[j], files[i]
                    i += 1
                    j -= 1
            return i, j

        def quick_sort_files(low, high):
            if low < high:
                i, j = partition(low, high)
                quick_sort_files(low, j)
                quick_sort_files(i, high)

        quick_sort_files(0, len(files) - 1)
        return files


        

    def isNewerThanFirstFile(self, file1, file2):
        if (int(file1[6:10]) < int(file2[6:10])):
            return True
        elif (int(file1[6:10]) > int(file2[6:10])):
            return False

        if (int(file1[3:5]) < int(file2[3:5])):
            return True
        elif (int(file1[3:5]) > int(file2[3:5])):
            return False

        if (int(file1[0:2]) < int(file2[0:2])):
            return True
        elif (int(file1[0:2]) > int(file2[0:2])):
            return False


        if (int(file1[11:13]) < int(file2[11:13])):
            return True
        elif (int(file1[11:13]) > int(file2[11:13])):
            return False

        if (int(file1[14:16]) < int(file2[14:16])):
            return True
        elif (int(file1[14:16]) > int(file2[14:16])):
            return False

        if (int(file1[17:19]) < int(file2[17:19])):
            return True
        elif (int(file1[17:19]) > int(file2[17:19])):
            return False



    def check_status_from_beginning(self):
        files = [f for f in os.listdir(self.storage_dir) if os.path.isfile(os.path.join(self.storage_dir,f))]
        print(files)
        print(files[0][3:5])



        







    def hash_function(self):
        return '1'
        



if __name__ == '__main__':
    struc = PatientRecord()
    #struc.add_node('add',None,[101,'Sri',False,['Disease1','Disease2']])
    struc.check_status_from_beginning()
