from blockchain import Blockchain
from uuid import uuid4
import threading
import time


class Node(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name,
        self.counter = counter
        self.node_identifier = str(uuid4()).replace('-', '')
        self.blockchain = Blockchain()
    
    def mine(self):
        # We run the proof of work algorithm to get the next proof...
        last_block = self.blockchain.last_block
        proof = self.blockchain.proof_of_work(last_block)
        
        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        self.blockchain.new_transaction(
            sender="0",
            recipient=self.node_identifier,
            amount=1,
        )
        
        # Forge the new Block by adding it to the chain
        previous_hash = self.blockchain.hash(last_block)
        block = self.blockchain.new_block(proof, previous_hash)
        
        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
        return response
    
    def new_transaction(self, values):
        # Check that the required fields are in the POST'ed data
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return 'Missing values', 400
        
        # Create a new Transaction
        index = self.blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
        
        response = {'message': f'Transaction will be added to Block {index}'}
        return response
    
    def chain(self):
        response = {
            'chain': self.blockchain.chain,
            'length': len(self.blockchain.chain),
        }
        return response
    
    def register_nodes(self, nodes):
        if nodes is None:
            return "Error: Please supply a valid list of nodes", 400
        
        for node in nodes:
            self.blockchain.register_node(node)
        
        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(self.blockchain.nodes),
        }
        return response
    
    def resolve_chains(self, all_chains):
        replaced = self.blockchain.resolve_conflicts(all_chains)
        
        if replaced:
            response = {
                'status': True,
                'message': 'Our chain was replaced',
                'new_chain': self.blockchain.chain
            }
        else:
            response = {
                'status': False,
                'message': 'Our chain is authoritative',
                'chain': self.blockchain.chain
            }
        
        return response
    
    def run(self):
        while True:
            print('thread_run', self.thread_id, self.name, self.counter)
            time.sleep(2)
