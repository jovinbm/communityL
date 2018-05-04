from node import Node
import threading
import csv
from time import time


def get_user_input_int(question_string, start_inclusive, end_inclusive, default):
    try:
        user_input = int(input(question_string))
    except:
        user_input = default
    
    if start_inclusive <= user_input <= end_inclusive:
        return user_input
    else:
        return default


def get_user_input_str(question_string, default):
    try:
        user_input = str(input(question_string))
    except:
        user_input = default
    return user_input


class Controller:
    def __init__(self):
        self.hardness = get_user_input_int('Hardness to use? 1-5:', 1, 5, 4)
        self.mining_mode = 'communityL' if get_user_input_int('Use communityL? 1=yes, 0=no(use normal):', 0, 1,
                                                              1) == 1 else 'normal'
        self.number_of_normal_nodes = get_user_input_int('How many normal nodes? 0-5:', 0, 5, 2)
        self.number_of_mining_pools = get_user_input_int('How many mining pools? 0-5:', 0, 5, 1)
        self.number_of_nodes_in_mining_pool = get_user_input_int('How many nodes in each mining pool? 0-5:', 0, 5, 2)
        self.nodes = []
        # normal nodes
        for i in range(0, self.number_of_normal_nodes):
            self.nodes.append(
                Node(
                    thread_id=i,
                    name="Node-" + str(i),
                    counter=i,
                    mining_mode=self.mining_mode
                )
            )
        
        # pool nodes
        for i in range(self.number_of_normal_nodes, self.number_of_normal_nodes + self.number_of_mining_pools):
            self.nodes.append(
                Node(
                    thread_id=i,
                    name="Node-" + str(i),
                    counter=i,
                    is_pool=True,
                    number_of_nodes=self.number_of_nodes_in_mining_pool,
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
        while not self.hardness < 1 and not counter > 10000:
            print('loop=', counter)
            now = time()
            
            for node_index in range(len(self.nodes)):
                node = self.nodes[node_index]
                self.chain_length_reference[node.thread_id] = len(node.chain()['chain'])
            
            # add same transactions to all
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
            
            # if mining mode is communityL, we resolve chains after each mine
            # since not doing so will also prevent individual miners
            # from mining
            if self.mining_mode == 'communityL' or counter % 5 == 0:
                # resolve chains
                all_chains = self.get_all_chains()
                winnings = []
                for node_index in range(len(self.nodes)):
                    node = self.nodes[node_index]
                    response = node.resolve_chains(all_chains)
                    result = {
                        'resolve_request': counter if self.mining_mode == 'communityL' else int(counter / 5) + 1,
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
            if counter % 1000 == 0:
                self.hardness -= 1
                self.change_hardness(self.hardness)
        
        print('Done!')


if __name__ == '__main__':
    controller = Controller()
    controller.run()
