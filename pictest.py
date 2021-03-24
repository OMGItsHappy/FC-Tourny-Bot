import pickle
from collections import defaultdict

tree = lambda : defaultdict(tree)
json = tree()
pickle.dump(json, open('test.p', 'wb'))
print(type(pickle.load(open('test.p', 'rb'))))