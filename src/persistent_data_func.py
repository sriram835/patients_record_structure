from collections import deque
import hashlib
import os
from datetime import datetime

class AVLNode:
    def __init__(self, patientData):
        self.data = patientData
        self.left = None
        self.right = None
        self.height = 1

class PatientRecord:
    def __init__(self):
        self.tree = None
        self.temp_root = None
        self.storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
        os.makedirs(self.storage_dir, exist_ok=True)

    def hash_input(self, data):
        if len(data) != 4:
            return "INVALID"
        
        pid = str(data[0])
        name_initial = data[1][0].upper() if data[1] else "_"
        cured_initial = "T" if data[2] else "F"
        disease_initial = "".join(d[0].lower() for d in data[3]) if data[3] else "_"

        return pid + name_initial + cured_initial + disease_initial
    
    def convert_str_to_data(self, data_str):
        try:
            res = data_str.split(' ')
            res[0] = int(res[0])
            res[2] = (res[2] == "True")
            diseases = res[3].strip('[]')
            if diseases:
                diseases = diseases.split(',')
            else:
                diseases = []
            res[3] = diseases
            return res
        except Exception:
            return None
    
    def level_order_traversal(self, root):
        if not root:
            return []
        
        result = []
        queue = deque([root])
        while queue:
            node = queue.popleft()
            if node:
                result.append(self.hash_input(node.data))
                queue.append(node.left)
                queue.append(node.right)

            else:
                result.append("None")

        return result
    
    def filter_invalid_files(self, files):
        valid_files = []
        for f in files:
            try:
                # Try to parse with datetime
                datetime.strptime(f, "%d-%m-%Y %H-%M-%S")
                valid_files.append(f)
            except ValueError:
                print(f"Invalid filename skipped: {f}")
        return valid_files
    
    def hash_function(self, root):
        traversal = self.level_order_traversal(root)
        traversal_str = ",".join(traversal)
        return hashlib.sha256(traversal_str.encode()).hexdigest()
    
    def sort_file_names(self, files):
            if not files:
                return []

            def is_earlier(file1, file2):
                dt1 = datetime.strptime(file1, "%d-%m-%Y %H-%M-%S")
                dt2 = datetime.strptime(file2, "%d-%m-%Y %H-%M-%S")
                return dt1 < dt2

            def partition(low, high):
                pivot = files[(low + high) // 2]
                i, j = low, high
                while i <= j:
                    while is_earlier(files[i], pivot):
                        i += 1
                    while is_earlier(pivot, files[j]):
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

        
    def rollback(self):
        files = [f for f in os.listdir(self.storage_dir) if os.path.isfile(os.path.join(self.storage_dir, f))]
        files = self.filter_invalid_files(files)
        files = self.sort_file_names(files)

        if len(files) < 2:
            print("no previous state to rollback to!")
            return  None
        
        previous_file = files[-2]
        previous_path = os.path.join(self.storage_dir, previous_file)

        with open(previous_path, 'r') as file:
            operation = file.readline().strip()
            old_data_str = None
            if operation == 'update':
                old_data_str = file.readline().strip()

            new_data_str = file.readline().strip()
            hash_cmd = file.readline().strip()
            hash_value = hash_cmd[6:] if hash_cmd.startswith("hash: ") else hash_cmd

        old_data = self.convert_str_to_data(old_data_str) if old_data_str else None
        new_data = self.convert_str_to_data(new_data_str)

        self.tree = AVLNode(new_data)
        computed_hash = self.hash_function(self.tree)
        
        if computed_hash == hash_value:
            print("Hash matches: integrity verified.")
        else:
            print("Hash mismatch: data may have been tampered!")

        print(f"Rolled back to node: {previous_file}")
        print("Operation: ", operation)
        if old_data:
            print("Old Data: ", old_data)
        print("New Data: ", new_data)
        print("Hash: ", hash_value)

        return {
            "operation":operation,
            "old_data":old_data,
            "new_data":new_data,
            "hash":hash_value
        }



