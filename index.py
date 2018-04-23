from node import Node
import threading
import csv
from time import time


class Controller:
    def __init__(self):
        self.hardness = 5
        self.mining_mode = 'our_pow'
        # self.mining_mode = ''
        self.nodes = []
        # normal nodes
        for i in range(0, 2):
            self.nodes.append(
                Node(
                    thread_id=i,
                    name="Node-" + str(i),
                    counter=i,
                    mining_mode=self.mining_mode
                )
            )
        
        # pool nodes
        for i in range(2, 3):
            self.nodes.append(
                Node(
                    thread_id=i,
                    name="Node-" + str(i),
                    counter=i,
                    is_pool=True,
                    number_of_nodes=2,
                    mining_mode=self.mining_mode
                )
            )
        
        self.chain_length_reference = {}
        
        # prepare files
        self.results_mining_times_fieldnames = [
            'mine_request',
            'mined',
            'hardness',
            'node_index',
            'node_name',
            'node_counter',
            'node_identifier',
            'blockchain_length',
            'is_pool',
            'number_of_nodes',
            'mining_time'
        ]
        with open(f'results_mining_times_{self.mining_mode}.csv', 'w+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.results_mining_times_fieldnames)
            writer.writeheader()
        
        self.winning_fieldnames = [
            'resolve_request',
            'hardness',
            'node_index',
            'node_name',
            'node_counter',
            'node_identifier',
            'blockchain_length',
            'is_pool',
            'number_of_nodes',
            'won'
        ]
        with open(f'winnings_{self.mining_mode}.csv', 'w+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.winning_fieldnames)
            writer.writeheader()
    
    def change_hardness(self, hardness):
        for i in range(len(self.nodes)):
            node = self.nodes[i]
            node.blockchain.hardness = hardness
    
    def get_all_chains(self):
        chains = []
        for i in range(len(self.nodes)):
            node = self.nodes[i]
            chains.append({
                'blockchain_id': node.thread_id,
                'chain': node.chain()['chain']
            })
        return chains
    
    def record_mining_times(self, results):
        with open(f'results_mining_times_{self.mining_mode}.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.results_mining_times_fieldnames)
            writer.writerows(results)
    
    def record_winnings(self, results):
        with open(f'winnings_{self.mining_mode}.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.winning_fieldnames)
            writer.writerows(results)
    
    def run(self):
        counter = 0
        while not self.hardness < 2 and not counter > 500:
            print('loop=', counter)
            now = time()
            
            if counter % 100 == 0:
                self.hardness -= 1
                self.change_hardness(self.hardness)
            
            for node_index in range(len(self.nodes)):
                node = self.nodes[node_index]
                self.chain_length_reference[node.thread_id] = len(node.chain()['chain'])
            
            # add transactions to all
            for node_index in range(len(self.nodes)):
                node = self.nodes[node_index]
                for i in range(3):
                    node.new_transaction({
                        "sender": "d4ee26eee15148ee92c6cd394edd974e",
                        "recipient": "someone-other-address",
                        "amount": 5
                    })
            
            # mine on all nodes
            threads = []
            for node_index in range(len(self.nodes)):
                node = self.nodes[node_index]
                if node.is_pool:
                    t = threading.Thread(target=node.minePool, args=())
                    t.daemon = True
                    t.start()
                    threads.append(t)
                else:
                    t = threading.Thread(target=node.mine, args=())
                    t.daemon = True
                    t.start()
                    threads.append(t)
            
            for thread_index in range(len(threads)):
                threads[thread_index].join()
            
            # record mining times
            mining_times = []
            for node_index in range(len(self.nodes)):
                node = self.nodes[node_index]
                chain = node.chain()['chain']
                mining_time = None
                if len(chain) < 2:
                    mining_time = chain[-1]['timestamp'] - now
                else:
                    mining_time = chain[-1]['timestamp'] - chain[-2]['timestamp']
                mined = len(chain) > self.chain_length_reference[node.thread_id]
                result = {
                    'mine_request': counter + 1,
                    'mined': mined,
                    'hardness': self.hardness,
                    'node_index': node.thread_id,
                    'node_name': node.name,
                    'node_counter': node.counter,
                    'node_identifier': node.node_identifier,
                    'blockchain_length': len(node.blockchain.chain),
                    'is_pool': node.is_pool,
                    'number_of_nodes': node.number_of_nodes,
                    'mining_time': '-' if not mined else mining_time
                }
                mining_times.append(result)
            self.record_mining_times(mining_times)
            
            # if mining mode is our_pow, we resolve chains after each mine
            # since not doing so will also prevent individual miners
            # from mining
            if self.mining_mode == 'our_pow' or counter % 5 == 0:
                # resolve chains
                all_chains = self.get_all_chains()
                winnings = []
                for node_index in range(len(self.nodes)):
                    node = self.nodes[node_index]
                    response = node.resolve_chains(all_chains)
                    result = {
                        'resolve_request': counter if self.mining_mode == 'our_pow' else int(counter / 5) + 1,
                        'hardness': self.hardness,
                        'node_index': node.thread_id,
                        'node_name': node.name,
                        'node_counter': node.counter,
                        'node_identifier': node.node_identifier,
                        'blockchain_length': len(node.blockchain.chain),
                        'is_pool': node.is_pool,
                        'number_of_nodes': node.number_of_nodes,
                        'won': not response['status']
                    }
                    winnings.append(result)
                    print(node.name, 'is_pool=' + str(node.is_pool), response['message'],
                          'length=' + str(node.chain()['length']))
                self.record_winnings(winnings)
            
            counter = counter + 1
        
        print('Done!')


if __name__ == '__main__':
    controller = Controller()
    controller.run()
