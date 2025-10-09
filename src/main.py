from collections import deque
from datetime import datetime
import os
import hashlib
import platform
import stat
import pickle

# ---------------- PERSON 1 & 2 & 3 LIBRARY CLASSES ----------------

class AVLNode:
    # Person 1: Node model for patients
    def __init__(self, patient_id, patient_name, is_cured, diseases):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.is_cured = is_cured
        self.diseases = diseases
        self.left = None
        self.right = None
        self.height = 1  # Person 1

class AVLPatientTree:
    def __init__(self):
        self.root = None  # Person 1

    # ---------- Utilities (Person 1) ----------
    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    # ---------- Rotations (Person 3) ----------
    def right_rotate(self, y):
        x, T2 = y.left, y.left.right
        x.right, y.left = y, T2
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x

    def left_rotate(self, x):
        y, T2 = x.right, x.right.left
        y.left, x.right = x, T2
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    # ---------- Insert / Search (Person 2) ----------
    def insert(self, patient_id, patient_name, is_cured, diseases):
        self.root = self._insert(self.root, patient_id, patient_name, is_cured, diseases)

    def _insert(self, node, patient_id, patient_name, is_cured, diseases):
        if not node:
            return AVLNode(patient_id, patient_name, is_cured, diseases)
        if patient_id < node.patient_id:
            node.left = self._insert(node.left, patient_id, patient_name, is_cured, diseases)
        elif patient_id > node.patient_id:
            node.right = self._insert(node.right, patient_id, patient_name, is_cured, diseases)
        else:
            return node
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        return self._balance(node)

    def _search(self, node, patient_id):
        if not node:
            return None
        if patient_id == node.patient_id:
            return node
        return self._search(node.left, patient_id) if patient_id < node.patient_id else self._search(node.right, patient_id)

    # ---------- Remove (Person 1) ----------
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
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            succ = self._get_min_value_node(node.right)
            node.patient_id, node.patient_name, node.is_cured, node.diseases = (
                succ.patient_id, succ.patient_name, succ.is_cured, succ.diseases
            )
            node.right = self._remove(node.right, succ.patient_id)
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        return self._balance(node)

    def _get_min_value_node(self, node):
        while node.left:
            node = node.left
        return node

    # ---------- Balance Logic (Person 1) ----------
    def _balance(self, node):
        bal = self.get_balance(node)
        if bal > 1:
            if self.get_balance(node.left) < 0:
                node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        if bal < -1:
            if self.get_balance(node.right) > 0:
                node.right = self.right_rotate(node.right)
            return self.left_rotate(node)
        return node

    # ---------- Update (Person 1) ----------
    def update(self, patient_id, new_name=None, new_is_cured=None, new_diseases=None):
        node = self._search(self.root, patient_id)
        if not node:
            return False
        if new_name is not None:
            node.patient_name = new_name
        if new_is_cured is not None:
            node.is_cured = new_is_cured
        if new_diseases is not None:
            node.diseases = new_diseases
        return True

    # ---------- Display & Validate (Person 3) ----------

    def display_tree(self):
        if not self.root:
            print("Tree is empty")
            return
        print("\n" + "="*50)
        print("PATIENT TREE (In-order)")
        print("="*50)
        self._inorder(self.root)

    def _inorder(self, node):
        if not node:
            return
        self._inorder(node.left)
        print(f"ID: {node.patient_id} | Name: {node.patient_name} | Cured: {node.is_cured} | Diseases: {', '.join(node.diseases)}")
        self._inorder(node.right)

    def check_avl_properties(self):
        h, ok = self._check_balance(self.root)
        print(f"{'✓ Balanced' if ok else '✗ Not balanced'} (Height: {h})")
        return ok

    def _check_balance(self, node):
        if not node:
            return 0, True
        lh, lb = self._check_balance(node.left)
        rh, rb = self._check_balance(node.right)
        h = max(lh, rh) + 1
        bal = lh - rh
        ok = lb and rb and abs(bal) <= 1
        if not ok:
            print(f" Imbalance at ID {node.patient_id}: factor {bal}")
        return h, ok

    # ---------- Parsing & File IO helpers ----------
    def _parse_line(self, line):
        try:
            parts = line.strip().split(' ', 3)
            patient_id = int(parts[0])
            patient_name = parts[1]
            is_cured = parts[2] == "True"
            diseases_str = parts[3][1:-1] if len(parts) > 3 else ""
            if diseases_str:
                diseases = [d.strip() for d in diseases_str.split(',') if d]
            else:
                diseases = []
            return (patient_id, patient_name, is_cured, diseases)
        except Exception:
            return None

    # --------- CONSTRUCT TREE FROM FILE ----------
    def construct_tree_from_file(self, filepath):
        # Keep behavior: empty root then insert lines
        self.root = None
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if line.strip() == "None":
                        continue
                    data = self._parse_line(line)
                    if data:
                        # Use the internal insert so balancing happens
                        self.root = self._insert(self.root, *data)
            return self.root
        return None

    def deconstruct_tree_to_file(self, filename):
        with open(filename, 'w') as file:
            if not self.root:
                return
            queue = deque([self.root])
            level_order_nodes = []
            while queue:
                node = queue.popleft()
                level_order_nodes.append(node)
                if node is not None:
                    queue.append(node.left)
                    queue.append(node.right)
            last_real_index = len(level_order_nodes) - 1
            while last_real_index >= 0 and level_order_nodes[last_real_index] is None:
                last_real_index -= 1
            level_order_nodes = level_order_nodes[:last_real_index + 1]
            for node in level_order_nodes:
                if node is None:
                    file.write("None\n")
                else:
                    diseases_str = ",".join(node.diseases)
                    line = f"{node.patient_id} {node.patient_name} {node.is_cured} [{diseases_str}]\n"
                    file.write(line)


# ---------------- PERSON 4 & 5 PERSISTENT STORAGE ----------------

class PatientRecord:
    def __init__(self):
        self.storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
        os.makedirs(self.storage_dir, exist_ok=True)
        self.tree_obj = AVLPatientTree()
        # load into tree_obj.root and also keep a quick reference to root
        current_path = os.path.join(self.storage_dir, 'current_tree')
        self.tree_obj.construct_tree_from_file(current_path)
        self.root = self.tree_obj.root
        
    def __del__(self):
        # Save the current tree to disk when object is destroyed
        current_path = os.path.join(self.storage_dir, 'current_tree')
        # make sure tree_obj.root reflects self.root
        self.tree_obj.root = self.root
        self.tree_obj.deconstruct_tree_to_file(current_path)
        print("Exiting...")

    def getCurrentTime(self):
        return datetime.now().strftime("%d-%m-%Y %H:%M:%S").replace(":", "-")

    def hash_input(self, data):
        pid, name, cured, diseases = data
        if len((pid, name, cured, diseases)) != 4:
            return "INVALID"
        ni = name[0].upper() if name else "_"
        ci = "T" if cured else "F"
        di = "".join(d[0].lower() for d in diseases) if diseases else "_"
        return f"{pid}{ni}{ci}{di}"

    def level_order_traversal(self, root):
        if not root:
            return []
        q, res = deque([root]), []
        while q:
            n = q.popleft()
            if n:
                res.append(self.hash_input((n.patient_id, n.patient_name, n.is_cured, n.diseases)))
                q.append(n.left); q.append(n.right)
            else:
                res.append("None")
        return res

    def hash_function(self, root):
        return hashlib.sha256(",".join(self.level_order_traversal(root)).encode()).hexdigest()

    def filter_invalid_files(self, files):
        out = []
        for f in files:
            try:
                # file names are timestamps like "08-10-2025 19-31-46"
                datetime.strptime(f, "%d-%m-%Y %H-%M-%S")
                out.append(f)
            except:
                pass
        return out

    def sort_file_names(self, files):
        return sorted(files, key=lambda f: datetime.strptime(f, "%d-%m-%Y %H-%M-%S"))

    def convert_data_to_str(self, d):
        pid, name, cured, dis = d
        return f"{pid} {name} {cured} [{','.join(dis)}]"

    def convert_str_to_data(self, s):
        parts = s.strip().split(' ', 3)
        pid = int(parts[0]); name = parts[1]; cured = (parts[2] == "True")
        dis = parts[3].strip("[]") if len(parts) > 3 else ""
        diseases = dis.split(',') if dis else []
        return [pid, name, cured, diseases]

    def add_node(self, operation, old_data, new_data):
        ts = self.getCurrentTime()
        # Ensure the tree object root matches self.root before hashing
        self.tree_obj.root = self.root
        h = self.hash_function(self.tree_obj.root)
        path = os.path.join(self.storage_dir, ts)
        with open(path,'w') as f:
            f.write(operation + "\n")
            if operation == "update":
                f.write(self.convert_data_to_str(old_data) + "\n")
            if new_data is not None:
                f.write(self.convert_data_to_str(new_data) + "\n")
            f.write("hash: " + h)
        mode = stat.S_IREAD if platform.system() == "Windows" else 0o444
        try:
            os.chmod(path, mode)
        except Exception:
            pass
        print(f"Added record {path}")

    def delete_sorted_data(self):
        files = [f for f in os.listdir(self.storage_dir) if os.path.isfile(os.path.join(self.storage_dir, f))]
        files = self.filter_invalid_files(files)
        files = self.sort_file_names(files)
        
        if not files:
            print("No data files found")
            return
        
        print(f"\nFound {len(files)} data files. Starting from FIRST inserted (oldest) to LAST inserted (newest)...")
        
        # Start from the FIRST file (oldest/earliest)
        index = 0
        
        while index < len(files):
            file_path = os.path.join(self.storage_dir, files[index])
            with open(file_path, 'r') as f:
                operation = f.readline().strip()
                if operation == "update":
                    old_line = f.readline().strip()
                current_line = f.readline().strip()
                patient_data = self.convert_str_to_data(current_line)
            
            print(f"\n[{index + 1}/{len(files)}] Delete patient: ID {patient_data[0]}, Name: {patient_data[1]}, Cured: {patient_data[2]}, Diseases: {patient_data[3]}")
            print(f"File: {files[index]} (Inserted: {files[index].replace('-', ':').replace(' ', ' at ')})")
            print(f"Operation: {operation}")
            
            # Only accept yes or no
            while True:
                choice = input("Delete this record? (yes/no): ").strip().lower()
                if choice in ['yes', 'y']:
                    try:
                        # Remove read-only attribute from file before deletion
                        try:
                            if platform.system() == "Windows":
                                os.chmod(file_path, stat.S_IWRITE)
                            else:
                                os.chmod(file_path, 0o644)
                        except Exception:
                            pass
                        
                        # PERMANENTLY DELETE THE FILE - NO BACKUP
                        os.remove(file_path)
                        print(f"✓ PERMANENTLY DELETED file: {files[index]}")
                        
                    except Exception as e:
                        print(f"✗ Error deleting file: {e}")
                    
                    index += 1
                    break
                    
                elif choice in ['no', 'n']:
                    print("Deletion stopped by user.")
                    return  # Return to menu immediately
                else:
                    print("Please answer only with 'yes' or 'no'")
            
            if index >= len(files):
                print("\n🎉 All files processed - storage is now empty!")
                break

    # ----------------- check_status_from_beginning (replay all files) -----------------
    def check_status_from_beginning(self):
        files = [f for f in os.listdir(self.storage_dir) if os.path.isfile(os.path.join(self.storage_dir, f))]
        files = self.filter_invalid_files(files)
        files = self.sort_file_names(files)
        print("History files:", files)

        temp_root = None
        index = 0

        while index < len(files):
            print("\n1. See Next Node\n2. Display Tree\n3. Stop")
            try:
                choice = int(input("Enter choice: "))
            except Exception:
                print("Invalid choice")
                continue

            if choice == 3:
                break

            if choice == 2:
                self.tree_obj.root = temp_root
                self.tree_obj.display_tree()
                continue

            file_path = os.path.join(self.storage_dir, files[index])
            with open(file_path, 'r') as node_file:
                old_patient_data = None
                operation = node_file.readline().strip()
                if operation == 'update':
                    old_line = node_file.readline().strip()
                    old_patient_data = self.convert_str_to_data(old_line) if old_line else None

                patient_line = node_file.readline().strip()
                if not patient_line:
                    print("Could not read data from file")
                    return False
                patient_data = self.convert_str_to_data(patient_line)

                hash_line = node_file.readline().strip()
                h = hash_line.split(" ",1)[1].strip() if hash_line and " " in hash_line else ""

                print(f"Operation done: {operation}")
                if old_patient_data:
                    print(f"Old patient data: {old_patient_data}")
                print(f"Current patient data: {patient_data}")

                # ---- use consistent tree_obj reference ----
                tree_obj = self.tree_obj

                if operation == 'add':
                    temp_root = tree_obj._insert(temp_root, *patient_data)
                elif operation == 'update':
                    node = tree_obj._search(temp_root, patient_data[0])
                    if node:
                        node.patient_name = patient_data[1]
                        node.is_cured = patient_data[2]
                        node.diseases = patient_data[3]
                    else:
                        return False
                elif operation == 'remove':
                    temp_root = tree_obj._remove(temp_root, patient_data[0])
                else:
                    print("No suitable operation")
                    return False

                # Verify hash
                new_hash = self.hash_function(temp_root)
                if new_hash != h:
                    print("⚠️ Persistent data corrupted (hash mismatch).")
                    return False

                index += 1

        print("Reached the end of files")
        return True


# ---------------- PERSON 3 INTERACTIVE TESTER ----------------

class InteractiveAVLTester:
    def __init__(self):
        self.tree = AVLPatientTree()
        self.records = PatientRecord()
        print("AVL Patient Tree Interactive Tester")
        print("="*40)

    def get_input(self):
        try:
            pid=int(input("Patient ID: "))
            name=input("Name: ").strip()
            ci=input("Cured? (y/n): ").strip().lower()
            cured=ci in ['y','yes']
            di=input("Diseases (comma sep): ").strip()
            dis=[d.strip() for d in di.split(',') if d.strip()] if di else []
            return pid,name,cured,dis
        except:
            print("Invalid"); return None

    def test_insert(self):
        d=self.get_input()
        if d:
            pid,name,cured,dis=d
            self.tree.insert(pid,name,cured,dis)
            self.records.root=self.tree.root
            self.records.add_node("add",None,[pid,name,cured,dis])
            print("Inserted",pid); self.tree.check_avl_properties()

    def test_update(self):
        try:
            pid=int(input("Update ID: "))
            n=self.tree._search(self.tree.root,pid)
            if not n: print("Not found"); return
            old=[n.patient_id,n.patient_name,n.is_cured,n.diseases.copy()]
            nn=input("New name(skip): ").strip() or None
            ci=input("New cured? (y/n skip): ").strip().lower()
            nic=True if ci in ['y','yes'] else False if ci in ['n','no'] else None
            di=input("New diseases(skip): ").strip()
            nd=[d.strip() for d in di.split(',') if d.strip()] if di else None
            ok=self.tree.update(pid,new_name=nn,new_is_cured=nic,new_diseases=nd)
            if ok:
                new=[pid,nn or old[1],nic if nic is not None else old[2],nd if nd else old[3]]
                self.records.root=self.tree.root
                self.records.add_node("update",old,new)
                print("Updated")
            else:
                print("Failed")
        except:
            print("Invalid")

    def test_remove(self):
        try:
            pid=int(input("Remove ID: "))
            n=self.tree._search(self.tree.root,pid)
            if not n: print("Not found"); return
            old=[n.patient_id,n.patient_name,n.is_cured,n.diseases.copy()]
            self.tree.remove(pid)
            self.records.root=self.tree.root
            self.records.add_node("remove",old,None)
            print("Removed",pid); self.tree.check_avl_properties()
        except:
            print("Invalid")

    def test_search(self):
        try:
            pid=int(input("Search ID: "))
            n=self.tree._search(self.tree.root,pid)
            if n: print("Found:",n.patient_name)
            else: print("Not found")
        except:
            print("Invalid")

    def rollback_to_previous_version(self):
            """
            Rollback by asking user "how many versions behind".
            Verifies every intermediate version's saved hash by replaying files.
            If verification succeeds, sets self.tree.root and self.records.root to the target root.
            """
            # load and sort valid files
            try:
                files = [f for f in os.listdir(self.records.storage_dir) if os.path.isfile(os.path.join(self.records.storage_dir, f))]
            except Exception as e:
                print(f"Could not access storage dir: {e}")
                return

            files = self.records.filter_invalid_files(files)
            files = self.records.sort_file_names(files)

            if len(files) < 2:
                print("No previous state (need at least 2 versions to rollback).")
                return

            print("\n📜 Available Versions (Oldest → Newest):")
            for idx, fn in enumerate(files, start=1):
                print(f" {idx}. {fn}")
            print(f"\n🔹 Current (latest) version: {files[-1]}")

            # get steps_back input
            try:
                steps_back = int(input(f"Enter how many versions behind to roll back (1 to {len(files)-1}): ").strip())
            except Exception:
                print("Invalid input. Rollback cancelled.")
                return

            if steps_back < 1 or steps_back >= len(files):
                print("Invalid rollback range. Rollback cancelled.")
                return

            # target index in files list (0-based)
            target_index = len(files) - (steps_back + 1)
            target_file = files[target_index]

            # Verify chain: for each version from latest (len(files)-1) down to target_index,
            # replay from beginning up to that version and ensure computed hash matches saved hash.
            # We will replay incrementally to avoid repeating work unnecessarily.
            temp_root = None
            for verify_i in range(0, len(files)):
                file_path = os.path.join(self.records.storage_dir, files[verify_i])
                try:
                    with open(file_path, 'r') as vf:
                        op = vf.readline().strip()
                        old_data = None
                        if op == "update":
                            old_line = vf.readline().strip()
                            old_data = self.records.convert_str_to_data(old_line) if old_line else None
                        # next line is new/current patient data
                        new_line = vf.readline().strip()
                        new_data = self.records.convert_str_to_data(new_line) if new_line else None
                        # next line contains 'hash: <h>'
                        hash_line = vf.readline().strip()
                        saved_hash = hash_line.split(" ", 1)[1].strip() if hash_line and " " in hash_line else ""
                except Exception as e:
                    print(f"Could not read version file {files[verify_i]}: {e}. Rollback aborted.")
                    return

                # Apply this file's operation to temp_root using low-level functions (so balancing works)
                if op == "add":
                    temp_root = temp_root = self.records.tree_obj._insert(temp_root, new_data[0], new_data[1], new_data[2], new_data[3])
                elif op == "update":
                    # find node; if present update fields, else insert (defensive)
                    node = self.records.tree_obj._search(temp_root, new_data[0])
                    if node:
                        node.patient_name = new_data[1]
                        node.is_cured = new_data[2]
                        node.diseases = new_data[3]
                    else:
                        temp_root = self.tree_obj._insert(temp_root, new_data[0], new_data[1], new_data[2], new_data[3])
                elif op == "remove":
                    temp_root = self.records.tree_obj._remove(temp_root, new_data[0])
                else:
                    print(f"Unknown operation '{op}' in file {files[verify_i]}. Rollback aborted.")
                    return

                # compute hash of temp_root and compare with saved_hash
                computed_hash = self.records.hash_function(temp_root)

                if computed_hash != saved_hash:
                    print(f"⚠️ Hash mismatch detected on version '{files[verify_i]}'.")
                    print("Rollback aborted to protect data integrity.")
                    return

                # If we've verified up to the target file (index), stop verifying further
                if verify_i == target_index:
                    break

            # If we reach here, all intermediate files up to target_index were valid.
            # temp_root currently equals the tree at target_index.
            # Apply to live trees (so future operations continue from here).
            self.records.root = temp_root
            self.records.tree_obj.root = temp_root
            self.tree.root = temp_root

            print(f"\n✅ Successfully rolled back {steps_back} version(s).")
            print(f"🔁 Now current version is: {files[target_index]}")
            # NOTE: we do not auto-create a new storage file here. The next add/update/remove will call add_node and create the next version.


    def delete_storage_data(self):
        self.records.delete_sorted_data()

    def run(self):
        while True:
            print("\nMenu: 1.Add 2.Update 3.Remove 4.Search 5.Display 6.RollBack 7.check_status_from_beginning 8.DeleteStorage 9.Exit")
            c=input("Choice: ").strip()
            if c=='1': self.test_insert()
            elif c=='2': self.test_update()
            elif c=='3': self.test_remove()
            elif c=='4': self.test_search()
            elif c=='5': self.tree.display_tree()
            elif c=='6': self.rollback_to_previous_version()
            elif c=='7': self.records.check_status_from_beginning()
            elif c=='8': self.delete_storage_data()
            elif c=='9': break
            else: print("Invalid")

if __name__=="__main__":
    InteractiveAVLTester().run()
