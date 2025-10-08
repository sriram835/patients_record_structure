import platform
import hashlib
import os
from datetime import datetime
import stat
from collections import deque

# ---------------- AVL Node (single definition used by everything) ----------------
class AVLNode:
    def __init__(self, patient_id, patient_name, is_cured, diseases):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.is_cured = is_cured
        self.diseases = diseases
        self.left = None
        self.right = None
        self.height = 1

# ---------------- PatientRecord (merged, minimal changes) ----------------
class PatientRecord:

############### Initializing the Data structure ####################
    def __init__(self):
        self.root = None
        self.temp_root = None
        # storage directory: same logic as provided (parent dir / storage)
        self.storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
        os.makedirs(self.storage_dir, exist_ok=True)

############### Hash Functions ####################
    def hash_input(self, data):
        if len(data) != 4:
            return "INVALID"
        
        pid = str(data[0])
        name_initial = data[1][0].upper() if data[1] else "_"
        cured_initial = "T" if data[2] else "F"
        disease_initial = "".join(d[0].lower() for d in data[3]) if data[3] else "_"
        return pid + name_initial + cured_initial + disease_initial

    def hash_function(self, root):
        traversal = self.level_order_traversal(root)
        traversal_str = ",".join(traversal)
        return hashlib.sha256(traversal_str.encode()).hexdigest()


    def level_order_traversal(self, root):
        if not root:
            return []
        
        result = []
        queue = deque([root])
        while queue:
            node = queue.popleft()
            if node:
                # Build data tuple as the other modules expect
                node_data = (node.patient_id, node.patient_name, node.is_cured, node.diseases)
                result.append(self.hash_input(node_data))
                queue.append(node.left)
                queue.append(node.right)
            else:
                result.append("None")

        return result


############### Utility Functions ####################
    def getCurrentTime(self):
        # Get current time and format as filename (DD-MM-YYYY HH-MM-SS)
        now = datetime.now()
        formatted_time = now.strftime("%d-%m-%Y %H:%M:%S")
        formatted_time = formatted_time.replace(':','-')
        return formatted_time


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


    def convert_str_to_data(self, data_str):
        try:
            res = data_str.strip().split(' ')
            # Expect exactly 4 parts; if patient_name contains spaces this will fail — but
            # we keep the parser as originally provided (minimal change).
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
        # Keep original comparison logic (minimal change)
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


    def filter_invalid_files(self, files):
        valid_files = []
        for f in files:
            try:
                # Try to parse with datetime; note: parser expects exact format
                datetime.strptime(f, "%d-%m-%Y %H-%M-%S")
                valid_files.append(f)
            except ValueError:
                print(f"Invalid filename skipped: {f}")
        return valid_files

    # Utility getters for height and balance (kept from provided code)
    def get_height(self, node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    # level_order generator (kept from provided code)
    def level_order(self):
        if not self.root:
            return
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            if node:
                yield node
                queue.append(node.left)
                queue.append(node.right)


############### Core Functions of Persistent Data Structure ####################
    def add_node(self,operation, old_data,new_data):
        timestamp = self.getCurrentTime()
        # compute hash over current tree structure (use self.root)
        node_hash = self.hash_function(self.root)
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
            node_file.write(node_hash)


        platform_type = platform.system()
        try:
            if (platform_type == 'Windows'):
                os.chmod(filePath,stat.S_IREAD)
            else:
                os.chmod(filePath,0o444)
        except Exception as e:
            # permission change might fail in some environments; keep minimal change
            print(f"Warning: could not change file permissions: {e}")

        print(f"Added node with name {filePath} and \nmade it readonly on platform: {platform_type}")
        return True


    def check_status_from_beginning(self):
        files = [f for f in os.listdir(self.storage_dir) if os.path.isfile(os.path.join(self.storage_dir,f))]
        files = self.filter_invalid_files(files)
        files = self.sort_file_names(files)
        
        self.temp_root = self.root
        self.root = None
        choice = 0
        index = 0
        
        while (choice != 3):
            print("1. See Next Node\n2.Display Tree\n3.Stop")
            try:
                choice = int(input("Enter choice: "))
            except Exception:
                print("Invalid choice")
                continue

            if choice == 3:
                break

            if choice == 2:
                self.displayTree(self.root)
                continue

            # NOTE: original code opened files[0]; keep same behavior (minimal change)
            with open(os.path.join(self.storage_dir,files[0]),'r') as node_file:

                old_patient_data = None
                operation = node_file.readline().strip()
                if operation == 'update':
                    old_patient_data = node_file.readline().strip()
                    old_patient_data = self.convert_str_to_data(old_patient_data)

                patient_data = node_file.readline().strip()
                patient_data = self.convert_str_to_data(patient_data)

                hash_line = node_file.readline().strip()
                hash_value = hash_line[6:] if hash_line.startswith('hash: ') else hash_line
                print(f"Operation done: {operation}")
                if old_patient_data is not None:
                    print(f"Old patient data:")
                    print(f"ID: {old_patient_data[0]}")
                    print(f"Name: {old_patient_data[1]}")
                    print(f"Is cured: {old_patient_data[2]}")
                    print(f"Diseases: {old_patient_data[3]}")

                print(f"Current patient data:")
                print(f"ID: {patient_data[0]}")
                print(f"Name: {patient_data[1]}")
                print(f"Is cured: {patient_data[2]}")
                print(f"Diseases: {patient_data[3]}")



    # --------- CONSTRUCT TREE FROM FILE ----------
    def construct_tree_from_file(self, filepath):
        # keep behavior: empty root then insert lines
        self.root = None
        with open(filepath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data = self._parse_line(line)
                if data:
                    self.root = self._insert(self.root, *data)

    def _parse_line(self, line):
        try:
            parts = line.strip().split(' ', 3)
            patient_id = int(parts[0])
            patient_name = parts[1]
            is_cured = parts[2] == "True"
            diseases_str = parts[3][1:-1]
            if diseases_str:
                diseases = [d.strip() for d in diseases_str.split(',') if d]
            else:
                diseases = []
            return (patient_id, patient_name, is_cured, diseases)
        except Exception:
            return None
 


############### Core functions for the AVL tree ####################
    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x


    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y


    # --------- REMOVE (DELETE PATIENT) ----------
    def remove(self, patient_id):
        self.root = self._remove(self.root, patient_id)


    def _remove(self, node, patient_id):
        if not node:
            return node
        if patient_id < node.patient_id:
            node.left = self._remove(node.left, patient_id)
        elif patient_id > node.patient_id:
            node.right = self._remove(node.right, patient_id)
        else:
            # Node to delete found
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Node with two children
            min_larger_node = self._get_min_value_node(node.right)
            node.patient_id = min_larger_node.patient_id
            node.patient_name = min_larger_node.patient_name
            node.is_cured = min_larger_node.is_cured
            node.diseases = min_larger_node.diseases
            node.right = self._remove(node.right, min_larger_node.patient_id)
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        return self._balance(node)


    def _get_min_value_node(self, node):
        while node.left:
            node = node.left
        return node


    def _balance(self, node):
        balance = self.get_balance(node)
        if balance > 1:
            if self.get_balance(node.left) >= 0:
                return self.right_rotate(node)
            else:
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)
        if balance < -1:
            if self.get_balance(node.right) <= 0:
                return self.left_rotate(node)
            else:
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)
        return node


    # --------- UPDATE PATIENT DATA ----------
    def update(self, patient_id, new_name=None, new_is_cured=None, new_diseases=None):
        node = self._search(self.root, patient_id)
        if node:
            if new_name is not None:
                node.patient_name = new_name
            if new_is_cured is not None:
                node.is_cured = new_is_cured
            if new_diseases is not None:
                node.diseases = new_diseases
            return True
        else:
            return False

    # --------- INSERT & SEARCH (copied from Group A, minimal add) ----------
    def insert(self, patient_id, patient_name, is_cured, diseases):
        # keep the same API as Group A
        self.root = self._insert(self.root, patient_id, patient_name, is_cured, diseases)

    def _insert(self, node, patient_id, patient_name, is_cured, diseases):
        if not node:
            return AVLNode(patient_id, patient_name, is_cured, diseases)
        if patient_id < node.patient_id:
            node.left = self._insert(node.left, patient_id, patient_name, is_cured, diseases)
        elif patient_id > node.patient_id:
            node.right = self._insert(node.right, patient_id, patient_name, is_cured, diseases)
        else:
            return node  # duplicate IDs not allowed
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        return self._balance(node)

    def _search(self, node, patient_id):
        if not node:
            return None
        if patient_id == node.patient_id:
            return node
        elif patient_id < node.patient_id:
            return self._search(node.left, patient_id)
        else:
            return self._search(node.right, patient_id)

 
############### Display Tree Functions ####################
    def displayTree(self,root):
        if root is None:
            return

        self.displayTree(root.left)
        print("\n------------------------------------")
        print(f"Patient ID: {root.patient_id}")
        print(f"Patient Name: {root.patient_name}")
        print(f"Is cured: {root.is_cured}")
        print(f"List of diseases {root.diseases}")
        print("------------------------------------\n")
        self.displayTree(root.right)


# ---------------- Example usage / test ----------------
if __name__ == '__main__':
    struc = PatientRecord()
    # Insert a patient (uses Group A insertion signature)
    struc.insert(101, 'Sri', False, ['Disease1','Disease2'])
    # Add a persistent node recording this addition (operation string, old_data, new_data)
    # Note: old_data is None for add
    struc.add_node('add', None, [101, 'Sri', False, ['Disease1','Disease2']])

    # Display current tree+
    struc.displayTree(struc.root)

    # Save tree to a file (deconstruct) — use same format as group2 function
    timestamp = struc.getCurrentTime()
    filepath = os.path.join(struc.storage_dir, timestamp + "_tree.txt")
    # Use deconstruct logic: reusing level_order generator and formatted line writing
    with open(filepath, 'w') as f:
        for node in struc.level_order():
            line = f"{node.patient_id} {node.patient_name} {node.is_cured} [{','.join(node.diseases)}]\n"
            f.write(line)
    print(f"Tree written to {filepath}")
