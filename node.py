from blockchain import Blockchain
from uuid import uuid4
import operator


class Node():
    def __init__(self, node_id, is_pool=False, number_of_nodes=1, mining_mode=None):
        self.node_id = node_id
        self.node_identifier = str(uuid4()).replace('-', '')
        self.blockchain = Blockchain(node_id)
        self.is_pool = is_pool
        self.number_of_nodes = number_of_nodes
        self.mining_mode = mining_mode
    
    def mineIndividual(self, qr):
        if self.mining_mode == 'communityL' and self.blockchain.chain[-1]['node_identifier'] == self.node_identifier:
            # not allowed to mine
            print(self.node_id, 'not mining')
            qr.put(None)
            return
        
        print(self.node_id, 'is mining')
        
        # We run the proof of work algorithm to get the next proof...
        last_block = self.blockchain.last_block
        (p, q) = self.blockchain.proof_of_work(last_block)
        
        # wait to finish ang get value
        p.join()
        work = q.get()
        q.close()
        
        # create block
        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        self.blockchain.new_transaction(
            sender="0",
            recipient=self.node_identifier,
            amount=1,
        )
        
        # Forge the new Block by adding it to the chain
        previous_hash = self.blockchain.hash(last_block)
        response = {
            'message': "New Block Forged",
            'new_block_recipe': {
                'proof': work['proof'],
                'previous_hash': previous_hash,
                'node_identifier': self.node_identifier,
                'timestamp': work['timestamp'],
            }
        }
        qr.put(response)
        print(self.node_id, 'done mining', 'chain length=', len(self.blockchain.chain) + 1)
    
    def minePool(self, qr):
        if self.mining_mode == 'communityL' and self.blockchain.chain[-1]['node_identifier'] == self.node_identifier:
            # not allowed to mine
            print(self.node_id, 'not mining')
            qr.put(None)
            return
        
        print(self.node_id, 'is mining')
        
        last_block = self.blockchain.last_block
        processes = []
        for node_index in range(self.number_of_nodes):
            # We run the proof of work algorithm to get the next proof...
            (p, q) = self.blockchain.proof_of_work(last_block)
            processes.append((p, q))
        
        # wait for each process to finish
        works = []
        for (p, q) in processes:
            p.join()
            work = q.get()
            q.close()
            works.append(work)
        
        works.sort(key=operator.itemgetter('timestamp'))
        work = works[0]
        
        # create block
        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        self.blockchain.new_transaction(
            sender="0",
            recipient=self.node_identifier,
            amount=1,
        )
        
        # Forge the new Block by adding it to the chain
        previous_hash = self.blockchain.hash(last_block)
        response = {
            'message': "New Block Forged",
            'new_block_recipe': {
                'proof': work['proof'],
                'previous_hash': previous_hash,
                'node_identifier': self.node_identifier,
                'timestamp': work['timestamp'],
            }
        }
        qr.put(response)
        print(self.node_id, 'done mining', 'chain length=', len(self.blockchain.chain) + 1)
    
    def new_transaction(self, values):
        # Check that the required fields are in the POST'ed data
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return 'Missing values', 400
        
        # Create a new Transaction
        index = self.blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
        
        response = {'message': f'Transaction will be added to Block {index}'}
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
        replaced = self.blockchain.resolve_conflicts(all_chains, mining_mode=self.mining_mode)
        
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
