from node import Node
import threading


class Controller:
    def __init__(self):
        self.nodes = []
        # normal nodes
        for i in range(0, 2):
            self.nodes.append(Node(i, "Node-" + str(i), i))
        
        # pool nodes
        for i in range(2, 3):
            self.nodes.append(Node(i, "Node-" + str(i), i, is_pool=True, number_of_nodes=2))
    
    def get_all_chains(self):
        chains = []
        for i in range(len(self.nodes)):
            node = self.nodes[i]
            chains.append({
                'blockchain_id': node.thread_id,
                'chain': node.chain()['chain']
            })
        return chains
    
    def run(self):
        counter = 0
        while True:
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
            
            if counter % 5 == 0:
                # resolve chains
                all_chains = self.get_all_chains()
                for node_index in range(len(self.nodes)):
                    node = self.nodes[node_index]
                    response = node.resolve_chains(all_chains)
                    print(node.name, 'is_pool=' + str(node.is_pool), response['message'],
                          'length=' + str(node.chain()['length']))
            
            counter = counter + 1


if __name__ == '__main__':
    controller = Controller()
    controller.run()
