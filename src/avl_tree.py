from collections import deque

class AVLNode:
    def __init__(self, patient_id, patient_name, is_cured, diseases):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.is_cured = is_cured
        self.diseases = diseases
        self.left = None
        self.right = None
        self.height = 1

class AVLPatientTree:
    def __init__(self):
        self.root = None

    # --------- UTILITY FUNCTIONS ----------
    def get_height(self, node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

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
        
    # --------- CONSTRUCT TREE FROM FILE ----------
    def construct_tree_from_file(self, filepath):
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

    # --------- DECONSTRUCT TREE TO FILE (LEVEL-ORDER) ----------
    def deconstruct_tree_to_file(self, filepath):
        with open(filepath, 'w') as file:
            for node in self.level_order():
                line = f"{node.patient_id} {node.patient_name} {node.is_cured} [{','.join(node.diseases)}]\n"
                file.write(line)

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

