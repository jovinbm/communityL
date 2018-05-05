## Installation

1. Make sure [Python 3.6+](https://www.python.org/downloads/) is installed. 
2. Install [pipenv](https://github.com/kennethreitz/pipenv). 

```
$ pip install pipenv 
```

3. Create a _virtual environment_ and specify the Python version to use. 

```
$ pipenv --python=python3.6
```

4. Install requirements.  

```
$ pipenv install 
``` 

5. Run:
    * `$ pipenv run python index.py` 
    * You will be prompted with several options that are required to run the experiment. In each experiment, 1000 
    iterations will run for each difficulty. 
    
## Key Files
    
 
There are three key files that you should focus your attention on.
 
`blockchain.py` contains the blockchain implementation including a reference to the current node's chain, functions to 
validate a chain, functions to resolve conflicts between multiple chains, block creation, transaction creation, 
computing and validating proof of work.

`node.py` contains helper functions used in the creation of nodes and pools of nodes (mining pools).To simulate multiple
nodes working simultaneously in the network, each node is executed in a separate process to prevent computation 
intensive operations like proof of work calculations from blocking another node's operations.

`index.py` is the entry point to our experiments and allows us to specify various difficulties to use in our testing. 
We can also switch between the normal blockchain consensus algorithm and CommunityL consensus algorithm. In addition to 
that, the user can also specify the type of nodes that should be in the network i.e. how many nodes and how many mining 
pools, and how many nodes should be present in each of the mining pools.

There are mainly two groups of results that we export for each particular experiment. The results of all experiments are
exported in `csv` format. Timing results are placed in files `results_mining_times_normal.csv` for experiments using 
the normal blockchain consensus algorithm and `results_mining_times_communityL.csv` for experiments using CommunityL 
consensus algorithm. Winning results are placed in `winnings_normal.csv` for experiments using the normal blockchain 
consensus algorithm and `winnings_communityL.csv` for experiments using CommunityL consensus algorithm.
 
## Parsing Results
- To parse mining time results: `python parser_mining_times.py`
- To parse winnings results: `python parser_winnings.py`