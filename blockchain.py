import hashlib
import json
from time import time
from urllib.parse import urlparse
import copy
import random
import multiprocessing
import math
import operator


class Blockchain:
    def __init__(self, blockchain_id):
        self.blockchain_id = blockchain_id
        self.hardness = 4
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)
    
    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
    
    def valid_chain(self, chain, mining_mode):
        last_block = chain[0]
        current_index = 1
        
        while current_index < len(chain):
            block = chain[current_index]
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], block['previous_hash']):
                return False
            
            last_block = block
            current_index += 1
        
        return True
    
    def resolve_conflicts(self, all_chains, mining_mode):
        new_chain = None
        # find the longest chains
        longests = []
        for i in range(len(all_chains)):
            chain_obj = all_chains[i]
            chain = chain_obj['chain']
            length = len(chain)
            if self.valid_chain(chain=chain, mining_mode=mining_mode):
                longests.append({
                    'length': length,
                    'chain_obj': chain_obj
                })
        longests.sort(key=operator.itemgetter('length'))
        longests.reverse()
        max_length = longests[0]['length']
        # remove all chains of lesser lengths
        longests = [c for c in longests if c['length'] == max_length]
        if len(longests) == 1:
            # meaning there was one that was longer than the others
            new_chain = longests[0]['chain_obj']
        else:
            # meaning there are multiple chains with the same max length
            # resolve the one with the least timestamp
            min_time = None
            min_time_index = None
            for i in range(len(longests)):
                chain_obj = longests[i]['chain_obj']
                chain = chain_obj['chain']
                if chain[-1]['timestamp'] < (min_time if min_time is not None else math.inf):
                    min_time = chain[-1]['timestamp']
                    min_time_index = i
            if min_time_index is not None:
                new_chain = longests[min_time_index]['chain_obj']
        
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain and new_chain['blockchain_id'] != self.blockchain_id:
            self.chain = copy.deepcopy(new_chain['chain'])
            return True
        else:
            return False
    
    def new_block(self, proof, previous_hash, node_identifier=None, timestamp=time()):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': timestamp,
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'node_identifier': node_identifier
        }
        
        # Reset the current list of transactions
        self.current_transactions = []
        
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        
        return self.last_block['index'] + 1
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    @staticmethod
    def hash(block):
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def _proof_of_work(self, last_block, q):
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        
        proof = random.randint(0, 2 ** 32)
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += random.randint(0, 2 ** 32)
        
        q.put({
            'proof': proof,
            'timestamp': time()
        })
    
    def proof_of_work(self, last_block):
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=self._proof_of_work, args=(last_block, q))
        p.daemon = True
        p.start()
        return (p, q)
    
    def valid_proof(self, last_proof, proof, last_hash):
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        
        hardness_string = ""
        for i in range(0, self.hardness):
            hardness_string += "0"
        
        return guess_hash[:self.hardness] == hardness_string
