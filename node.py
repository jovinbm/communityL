from blockchain import Blockchain
from uuid import uuid4
import threading
import queue


class Node(threading.Thread):
    def __init__(self, thread_id, name, counter, is_pool=False, number_of_nodes=1, mining_mode=None):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name,
        self.counter = counter
        self.node_identifier = str(uuid4()).replace('-', '')
        self.blockchain = Blockchain(thread_id)
        self.is_pool = is_pool
        self.number_of_nodes = number_of_nodes
        self.mining_mode = mining_mode
    
    def mine(self, q=None, mine_lock=None):
        if self.mining_mode == 'our_pow' and self.blockchain.chain[-1]['node_identifier'] == self.node_identifier:
            # not allowed to mine
            return
        
        if q is None:
            q = queue.Queue()
        if mine_lock is None:
            mine_lock = threading.Lock()
        
        # We run the proof of work algorithm to get the next proof...
        last_block = self.blockchain.last_block
        proof = self.blockchain.proof_of_work(last_block)
        
        if mine_lock.acquire(blocking=True):
            q.put(None)
            if q.qsize() > 1:
                # somebody else completed before us
                mine_lock.release()
                return None
            
            # We must receive a reward for finding the proof.
            # The sender is "0" to signify that this node has mined a new coin.
            self.blockchain.new_transaction(
                sender="0",
                recipient=self.node_identifier,
                amount=1,
            )
            
            # Forge the new Block by adding it to the chain
            previous_hash = self.blockchain.hash(last_block)
            block = self.blockchain.new_block(proof, previous_hash, node_identifier=self.node_identifier)
            
            response = {
                'message': "New Block Forged",
                'index': block['index'],
                'transactions': block['transactions'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
            }
            mine_lock.release()
            return response
    
    def minePool(self):
        q = queue.Queue()
        mine_lock = threading.Lock()
        for node_index in range(self.number_of_nodes):
            t = threading.Thread(target=self.mine, args=(q, mine_lock))
            t.daemon = True
            t.start()
    
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
        self.mine()
