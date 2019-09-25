import shelve
 
test = {'a': 1, 'b': 2}
 
bd = shelve.open('save\\data.db')
bd['test'] = test
bd.close()

bd = shelve.open('save\\data.db')
print(bd['test'])
bd.close()