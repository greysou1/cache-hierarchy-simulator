import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Cache parameters')
    parser.add_argument('--BLOCKSIZE', type=int, default=32, help='Positive integer. Block size in bytes.')
    parser.add_argument('--L1_SIZE', type=int, default=8192, help='Positive integer. L1 cache size in bytes.')
    parser.add_argument('--L1_ASSOC', type=int, default=4, help='Positive integer. L1 set-associativity (1 is direct-mapped).')
    parser.add_argument('--L2_SIZE', type=int, default=262144, help='Positive integer. L2 cache size in bytes. L2_SIZE = 0 signifies that there is no L2 cache.')
    parser.add_argument('--L2_ASSOC', type=int, default=8, help='Positive integer. L2 set-associativity (1 is direct-mapped).')
    parser.add_argument('--REPLACEMENT_POLICY', type=int, default=0, help='Positive integer. 0 for LRU, 1 for FIFO, 2 for optimal.')
    parser.add_argument('--INCLUSION_PROPERTY', type=int, default=0, help='Positive integer. 0 for non-inclusive, 1 for inclusive.')
    parser.add_argument('--trace_file', type=str, default='traces/compress_trace.txt', help='Character string. Full name of trace file including any extensions.')

    args = parser.parse_args()

    return vars(args)

def validate_params(params):
    for key, value in params.items():
        if(key == 'trace_file'):
            if(not os.path.exists(value)):
                print('Given file path: {value} does not exist!')
                return False
        else:
            if(int(value) < 0):
                print(f'ERROR! {key} should be > 0.')
                return False
    
    return True
def print_params(params):
    print(('='*14)+(' Cache Config ')+('='*14))
    for key, value in params.items():
        if key == 'REPLACEMENT_POLICY':
            if value == 0:
                value = 'LRU'
            elif value == 1:
                value = 'FIFO'
            elif value == 2:
                value == 'Optimal'
        
        if key == 'INCLUSION_PROPERTY':
            if value == 0:
                value = 'Non-inclusive'
            elif value == 1:
                value = 'Inclusive'
            else:
                print('ERROR! Invalid input for inclusion policy. (0: non-inclusive, 1: inclusive)')
        
        whitespace1 = int((42/2) - (len(key)))
        whitespace2 = int((42/2) - (len(str(value)) + 2))
        if key != 'trace_file':
            print(f'{key}'+' '*whitespace1+':'+' '*whitespace2+f' {value}')
    print(('='*(14+14+14)))

def h2b(hex):
    return bin(int(hex, 16)).zfill(8)

def b2d(binary):
    return int(binary, 2)

def print_set(set):
    set_list = []
    for block in set:
        block_dict = {}
        # block_dict['valid'] = block.valid
        # block_dict['dirty'] = block.dirty
        block_dict['tag'] = block.tag
        # block_dict['addr'] = block.addr
        block_dict['access_count'] = block.access_count

        set_list.append(block_dict)
    print(set_list)