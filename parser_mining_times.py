import csv

mining_times_individual_nodes = []
mining_times_pools = []
not_mined_individual_nodes = 0
not_mined_pools = 0


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

with open('results_mining_times_communityL.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row['hardness']) != hardness:
            continue
        
        if row['mining_time'] == '-':
            if int(row['node_index']) == 2:
                not_mined_pools += 1
            else:
                not_mined_individual_nodes += 1
            continue
        
        if int(row['node_index']) == 2:
            mining_times_pools.append(float(row['mining_time']))
        else:
            mining_times_individual_nodes.append(float(row['mining_time']))

print('Number of times individual nodes did not mine: ', not_mined_individual_nodes)
print('Number of times pools did not mine: ', not_mined_pools)
print('Average mining times for individual nodes: ',
      sum(mining_times_individual_nodes) / float(len(mining_times_individual_nodes)))
print('Average mining times for pools: ', sum(mining_times_pools) / float(len(mining_times_pools)))
