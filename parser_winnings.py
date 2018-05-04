import csv

number_of_wins_individual_nodes = 0
number_of_wins_pools = 0


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

with open('winnings_communityL.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row['hardness']) != hardness:
            continue
        
        if int(row['node_index']) == 2:
            if int(row['won']) == 1:
                number_of_wins_pools += 1
        else:
            if int(row['won']) == 1:
                number_of_wins_individual_nodes += 1

print('Number of wins individual nodes: ', number_of_wins_individual_nodes)
print('Number of wins pools: ', number_of_wins_pools)
