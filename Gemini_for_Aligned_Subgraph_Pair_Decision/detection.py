# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from graphnnSiamese import graphnn
from utils import *
import os
import argparse
import json
import io

def processing_function(config):
    file_config_pair, file_path, write_json_file = config
    package_name = file_config_pair[:file_config_pair.find('_')]
    arch1 = file_config_pair[file_config_pair.find('_')+1:file_config_pair.find('-')]
    arch2 = file_config_pair[file_config_pair.find('-')+1:]

    gnn, BATCH_SIZE = load_model()

    with open(file_path) as inf:
        for line in inf:
            info = json.loads(line.strip())
            fname = info['fname']
            binary_file1 = info['binary_file1']
            binary_file2 = info['binary_file2']
            if package_name == 'coreutils':
                sub_path1 = package_name+'-'+arch1+'/'+binary_file1
                sub_path2 = package_name+'-'+arch2+'/'+binary_file2
            elif package_name == 'diffutils':
                sub_path1 = package_name+'-3.6-'+arch1+'/'+binary_file1
                sub_path2 = package_name+'-3.6-'+arch2+'/'+binary_file2
            elif package_name == 'findutils':
                sub_path1 = package_name+'-4.6-'+arch1+'/'+binary_file1
                sub_path2 = package_name+'-4.6-'+arch2+'/'+binary_file2
            g1_succs, g1_features = get_acfg(fname, ACFG_FILE_PATH+'/'+sub_path1)
            g2_succs, g2_features = get_acfg(fname, ACFG_FILE_PATH+'/'+sub_path2)
            subg1s = info['subgraph_pair']['subg1s'] 
            subg2s = info['subgraph_pair']['subg2s']

            item = {'fname':fname, 'binary_file1':binary_file1, 'binary_file2':binary_file2}
            item["similarities"] = []
            
            for i in range(len(subg1s)):
                subg1 = subg1s[i]
                subg2 = subg2s[i]
                g1 = get_g(subg1, g1_succs, g1_features)
                g2 = get_g(subg2, g2_succs, g2_features)

                X1, X2, m1, m2 = get_pair(g1, g2, BATCH_SIZE) 
                diff = gnn.calc_diff(X1, X2, m1, m2)
                diff = np.array(list(diff)) 
                similarity = (1-diff[0])/2
                item["similarities"].append(similarity)


            item = json.dumps(item, ensure_ascii=False) 
            try:
                if not os.path.exists(write_json_file):
                    with io.open(write_json_file, "w", encoding='utf-8') as f: 
                        f.write(item + "\n")
                else:
                    with io.open(write_json_file, "a", encoding='utf-8') as f:
                        f.write(item + "\n")
            except Exception as e:
                print("write error==>", e)
                

if __name__ == '__main__':
    cur_dir = "./"

    detected_pairs_path = cur_dir+'detected_candidate_subgraph_pairs_results/'
    
    pairs_similarity_path = cur_dir+'candidate_subgraph_pairs_similarity_results/'
    if not os.path.exists(pairs_similarity_path):
        os.makedirs(pairs_similarity_path)
    ACFG_FILE_PATH = cur_dir+'read_acfg_result_new/'

    for filename in os.listdir(detected_pairs_path):
        file_path = detected_pairs_path+filename
        write_json_file = pairs_similarity_path+filename
        if os.path.exists(write_json_file):
            continue
        processing_function([filename.replace('.json', ''), file_path, write_json_file])

