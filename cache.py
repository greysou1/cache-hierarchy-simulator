# 1: take command line arguments
# 2: read the input trace file
# 3: create a cache class
    # a: cache config
    # b: cache data structure based on the given size and associativity
# 4: initialise L1 and L2 cache
# 5: write policy
# 6: replacement policy
# 7: inclusion

from audioop import add
import numpy as np
import argparse
from helper import *
from math import log2

class Block:
    def __init__(self):
        self.valid = 0 # 0 = empty, 1 = used
        self.dirty = 0 # the block is not available in the next level
        self.tag = 0 # tag of the data
        self.addr = 0 # address of the data
        self.access_count = 0 # count the number of time the data is accessed

class Cache:
    def __init__(self, cache_size, block_size, cache_assoc, level=1, rep_policy=0, inc_prop=0):
        self.cache_size = cache_size
        self.block_size = block_size
        self.cache_assoc = cache_assoc
        self.rep_policy = rep_policy
        self.inc_prop = inc_prop
        self.level = level
        self.max_index = 0
        self.dirty_block = Block()

        num_cache_blocks = int(cache_size/block_size)
        sets = int(num_cache_blocks/cache_assoc)
        print(f'L{level}: {num_cache_blocks = }, {sets = }, {cache_assoc = }')

        # assoc_indexes = [0] * sets
        self.cache = [[Block() for j in range(cache_assoc)] for i in range(sets)]
        print(f'L{level} cache initialised!')

    def write(self, addr):
        tag, index, offset = self.get_addr_data(addr)
        hit = 0
        tag_in_set_index = self.tag_in_set(tag, self.cache[index])
        if tag_in_set_index > -1: # check if the tag is already present in the set
            top_r = self.get_top_r_count(self.cache[index])
            self.cache[index][tag_in_set_index].access_count = top_r + 1
            hit = 1
            return hit

        top_r = self.get_top_r_count(self.cache[index])
        # go through all the ways (blocks) in the current set of index
        for i, block in enumerate(self.cache[index]):
            # if Block.valid = 0, empty block
            # fill block, make it valid
            if not block.valid:
                block.valid = 1
                block.addr = addr
                block.tag = tag
                block.dirty = 1
                if self.rep_policy == 0:
                    # LRU                   
                    block.access_count += 1
                elif self.rep_policy == 1:
                    # FIFO
                    block.access_count = top_r + 1

                self.cache[index][i] = block
                hit = 1
                return hit
        
        # if all the Block.valid = 1, the set is full
        # replacement policy
        # since the required block isn't in the set it's a miss
        # we're going to replace this block and since it's dirty
        # we'll store it in L2.cache

        r_block_index = self.get_replacement_block(self.cache[index])

        block = self.cache[index][r_block_index]
        # print(f'[{index}, {r_block_index}]: {block.dirty = }, {block.access_count = }, {block.valid = }')
        if block.dirty == 1:
            self.dirty_block = block
            # print(f'{block.addr = }')

        # update the block with the new addr data                    
        block.addr = addr
        block.tag = tag
        block.dirty = 1
        if self.rep_policy == 0:
            # Least Recently Used                   
            block.access_count += 1
        elif self.rep_policy == 1:
            # First In First Out
            block.access_count = top_r + 1
        
        self.cache[index][r_block_index] = block
        
        hit = 0 
        return hit
        # elif self.rep_policy == 2:
        #     # Optimal
        #     pass
  
        return hit
        
    def read():
        pass

    def get_replacement_block(self, set):
            '''
            given a set, the function returns the index of the block with the least access_count
            '''
            replacement_index = 0
            for i, block in enumerate(set):  
                if block.access_count < set[replacement_index].access_count:
                    replacement_index = i

            return replacement_index

    def get_fifo_block(self, set):
        '''
        given a set, the function returns the first in block
        '''
        lru_index = 0
        for i, block in enumerate(set):  
            if block.access_count < set[lru_index].access_count:
                lru_index = i

        return lru_index 

    def get_addr_data(self, addr):
        '''
        computes and returns the tag, index, offset of the given address
        '''
        if not type(addr) == type('str'):
            print(f'{self.level = }')
            print(addr)
        num_sets = self.cache_size / (self.cache_assoc * self.block_size)
        index_bits = int(log2(num_sets))
        offset_bits = int(log2(self.block_size))
        tag_bits = int(32 - index_bits - offset_bits)
        # print(f' {tag_bits = }, {index_bits = }, {offset_bits = }')

        offset = int(addr[-offset_bits:])
        index = int(b2d(addr[-(index_bits+offset_bits): -offset_bits]))
        tag = addr[0: tag_bits]

        if index > self.max_index:
            self.max_index = index
        # print(f'{len(tag) =  }, {index = }, {offset = }')
        # print(f'{tag =  }, {index = }, {offset = }')

        return tag, index, offset

    def tag_in_set(self, tag, set):
        '''
        checks if the block with the given tag is already in the given set
        '''
        index = -1
        for i, block in enumerate(set):
            if block.tag == tag:
                index = i
                return index
        
        return index

    def get_top_r_count(self, set):
        top_r = 0
        for block in set:
            if block.access_count > top_r:
                top_r = block.access_count

        return top_r

    def print_cache(self):
        # cache_list = []
        for set in self.cache:
            set_list = []
            for block in set:
                block_dict = {}
                block_dict['valid'] = block.valid
                block_dict['dirty'] = block.dirty
                block_dict['tag'] = block.tag
                block_dict['addr'] = block.addr
                block_dict['access_count'] = block.access_count

                set_list.append(block_dict)
            print(set_list)
            


if __name__ == '__main__':
    # get configurable cache parameters from the user (cmd line)
    cache_params = parse_args() 
    if validate_params(cache_params):
        print_params(cache_params)

    L1 = Cache(cache_params['L1_SIZE'], cache_params['BLOCKSIZE'], cache_params['L1_ASSOC'], rep_policy=cache_params['REPLACEMENT_POLICY'], inc_prop=cache_params['INCLUSION_PROPERTY'], level=1)
    L2 = Cache(cache_params['L2_SIZE'], cache_params['BLOCKSIZE'], cache_params['L2_ASSOC'], rep_policy=cache_params['REPLACEMENT_POLICY'], inc_prop=cache_params['INCLUSION_PROPERTY'], level=2)

    i = 0
    with open(cache_params['trace_file'], 'r') as f:
        trace_file = f.readlines()

    
    writes = 0
    L1_hits, L2_hits = 0, 0
    for line in trace_file:    
        i += 1
        op, addr = line.split(' ', 1)
        addr = h2b(addr)
        # print(op, addr)

        
        
        if op == 'w': # handles write operations
            L1_hit = L1.write(addr)
            if L1_hit:
                writes += 1
                # print('L1 hit')
                L1_hits += 1
            else:
                # L1 miss
                # write-back policy 
                # get the dirty block from L1 and store it in L2
                
                L2.write(L1.dirty_block.addr)
                L2_hits += 1
        else:
            # print('skipping')
            pass

    print(f'{i = }, {writes = }, {L1_hits = }, {L2_hits = }')
    L1.print_cache()
    print('=' * 20)
    L2.print_cache()
        