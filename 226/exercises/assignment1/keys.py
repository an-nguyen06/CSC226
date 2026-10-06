import random, csv

# This file generates random keys for insertions and unsuccessful searches 
# for the hash table with chaining experiment. It creates CSV files for each 
# load factor containing the keys to be used in the experiment. 

m = 100000
alphas = [0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]

for a in alphas:
    n = int(a*m)

    insert_keys = random.sample(range(10**7), n)
    unsuccessful_keys = random.sample(range(10**7, 2*10**7), n)

    with open(f"insert_{a}.csv", "w", newline="") as f:
        w = csv.writer(f)
        for k in insert_keys:
            w.writerow([k])

    with open(f"unsuccessful_{a}.csv", "w", newline="") as f:
        w = csv.writer(f)
        for k in unsuccessful_keys:
            w.writerow([k])