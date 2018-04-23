from node import Node


class Controller:
    def __init__(self):
        self.nodes = []
        self.node1 = Node(1, "Thread-1", 1)
        self.node2 = Node(2, "Thread-2", 2)
        self.nodes.append(self.node1)
        self.nodes.append(self.node2)
    
    def get_all_chains(self):
        chains = []
        for i in range(len(self.nodes)):
            node = self.nodes[i]
            chains.append(node.chain()['chain'])
        return chains
    
    def run(self):
        counter = 0
        while True:
            self.node1.mine()
            self.node1.mine()
            self.node1.mine()
            self.node2.mine()
            self.node2.mine()
            if counter % 5 == 0:
                all_chains = self.get_all_chains()
                response1 = self.node1.resolve_chains(all_chains)
                response2 = self.node2.resolve_chains(all_chains)
                print('node1', response1['message'])
                print('node2', response2['message'])
            print('node1-chain', self.node1.chain()['length'])
            print('node2-chain', self.node2.chain()['length'])
            counter = counter + 1


if __name__ == '__main__':
    controller = Controller()
    controller.run()
