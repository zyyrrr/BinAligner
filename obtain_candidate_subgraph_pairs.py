import os
import json
from find_candidate_subgraph_pairs import *


def get_acfg(func_name, sub_path):
    succs = ''
    with open(cur_dir+'GroundTruth/read_acfg_result/'+sub_path) as inf:
        for line in inf:
            info = json.loads(line.strip())
            if func_name == info['fname']:
                succs = info['succs']
                break
    return succs


def save_file(path, func_name, sub_g1s, sub_g2s, binary_file1, binary_file2):
    item = {'fname':func_name, 'binary_file1':binary_file1, 'binary_file2':binary_file2}
    item["subgraph_pair"] = {"subg1s": [], "subg2s": []}
    for sub_g1 in sub_g1s:
        item["subgraph_pair"]["subg1s"].append(sub_g1.toSave())
    for sub_g2 in sub_g2s:
        item["subgraph_pair"]["subg2s"].append(sub_g2.toSave())
        
    item = json.dumps(item)
    try:
        if not os.path.exists(path):
            with open(path, "w", encoding='utf-8') as f: 
                f.write(item + "\n")
                # print("^_^ write success")
        else:
            with open(path, "a", encoding='utf-8') as f:
                f.write(item + "\n")
                # print("^_^ write success")
    except Exception as e:
        print("write error==>", e)


def processing(file_config_pair):
    save_subgraphs_file = save_subgraphs_dir+file_config_pair+'.json'

    package_name = file_config_pair[:file_config_pair.find('_')]
    arch1 = file_config_pair[file_config_pair.find('_')+1:file_config_pair.find('-')]
    arch2 = file_config_pair[file_config_pair.find('-')+1:]

    with open(text_comparison_results_dir+file_config_pair+'/lineno_map.json') as inf: 
        for line in inf:
            info = json.loads(line.strip())
            fname = info['fname']
            lineno_map = info['lineno_map']
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
            g1_succs = get_acfg(fname, sub_path1)
            g2_succs = get_acfg(fname, sub_path2)

            sub_g1s, sub_g2s = find_candidate_subgraph_pairs(g1_succs, g2_succs) 

            if sub_g1s != None: 
                save_file(save_subgraphs_file, fname, sub_g1s, sub_g2s, binary_file1, binary_file2)


if __name__ == "__main__":

    environment = "CrossArch" 
    cur_dir = "./"

    text_comparison_results_dir = cur_dir+'GroundTruth/text_comparison_results/'+environment+'/'
    save_subgraphs_dir = cur_dir+'candidate_subgraph_pairs_results/'
    if not os.path.isdir(save_subgraphs_dir):
        os.makedirs(save_subgraphs_dir)
        
    for subdirectory in os.listdir(text_comparison_results_dir): 
        processing(subdirectory)        