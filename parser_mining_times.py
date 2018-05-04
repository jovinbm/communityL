import csv

mining_times_individual_nodes = []
mining_times_pools = []
not_mined_node0 = 0
not_mined_node1 = 0
not_mined_node2 = 0


def get_user_input_int(question_string, start_inclusive, end_inclusive, default):
    try:
        user_input = int(input(question_string))
    except:
        user_input = default
    
    if start_inclusive <= user_input <= end_inclusive:
        return user_input
    else:
        return default


hardness = get_user_input_int('What hardness to extract data for? 1-4: ', 1, 4, -1)

with open('results_mining_times_normal.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row['hardness']) != hardness:
            continue
        
        if row['mining_time'] == '-':
            if int(row['node_index']) == 0:
                not_mined_node0 += 1
            if int(row['node_index']) == 1:
                not_mined_node1 += 1
            if int(row['node_index']) == 2:
                not_mined_node2 += 1
        else:
            if int(row['node_index']) == 2:
                mining_times_pools.append(float(row['mining_time']))
            else:
                mining_times_individual_nodes.append(float(row['mining_time']))

print('Number of times node 0 did not mine: ', not_mined_node0)
print('Number of times node 1 did not mine: ', not_mined_node1)
print('Number of times node 2 (pool) did not mine: ', not_mined_node2)
print('Average mining times for individual nodes: ',
      sum(mining_times_individual_nodes) / float(len(mining_times_individual_nodes)))
print('Average mining times for pools: ', sum(mining_times_pools) / float(len(mining_times_pools)))
