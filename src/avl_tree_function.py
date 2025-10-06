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