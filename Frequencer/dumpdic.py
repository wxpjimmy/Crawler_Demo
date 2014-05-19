from frequencer.dbadapter import DBAdapter
from settings import *
import time

start = time.time()
opts = DBAdapter('root', 'hohoyi123')
opts.dump_all()
cost = (time.time() - start) * 1000.0
print("Total cost(ms) for dumping is: %0.3f" % cost)