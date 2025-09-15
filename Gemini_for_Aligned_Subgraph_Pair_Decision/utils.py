# -*- coding: utf-8 -*-
import os
import io
import json
import copy
import random
import argparse
import numpy as np
import tensorflow as tf
print tf.__version__
from sklearn.metrics import auc, roc_curve
from graphnnSiamese import graphnn


def load_model():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=str, default='1',
            help='visible gpu device')
    parser.add_argument('--fea_dim', type=int, default=7,
            help='feature dimension')
    parser.add_argument('--embed_dim', type=int, default=64,
            help='embedding dimension')
    parser.add_argument('--embed_depth', type=int, default=2,
            help='embedding network depth')
    parser.add_argument('--output_dim', type=int, default=64,
            help='output layer dimension')
    parser.add_argument('--iter_level', type=int, default=5,
            help='iteration times')
    parser.add_argument('--lr', type=float, default=1e-4,
            help='learning rate')
    parser.add_argument('--epoch', type=int, default=100,
            help='epoch number')
    parser.add_argument('--batch_size', type=int, default=1,
            help='batch size')
    parser.add_argument('--load_path', type=str,
            default='./saved_model/graphnn-model_best',
            help='path for model loading, "#LATEST#" for the latest checkpoint')
    parser.add_argument('--log_path', type=str, default='./saved_log/detection.log',
            help='path for testing log')

    args = parser.parse_args([])
    args.dtype = tf.float32
    print("=================================")
    print(args)
    print("=================================")

    os.environ["CUDA_VISIBLE_DEVICES"]=args.device 
    
    Dtype = args.dtype
    NODE_FEATURE_DIM = args.fea_dim
    EMBED_DIM = args.embed_dim
    EMBED_DEPTH = args.embed_depth
    OUTPUT_DIM = args.output_dim
    ITERATION_LEVEL = args.iter_level
    LEARNING_RATE = args.lr
    MAX_EPOCH = args.epoch
    BATCH_SIZE = args.batch_size
    LOAD_PATH = args.load_path
    LOG_PATH = args.log_path

    # Model
    gnn = graphnn(
            N_x = NODE_FEATURE_DIM,
            Dtype = Dtype, 
            N_embed = EMBED_DIM,
            depth_embed = EMBED_DEPTH,
            N_o = OUTPUT_DIM,
            ITER_LEVEL = ITERATION_LEVEL,
            lr = LEARNING_RATE
        )
    gnn.init(LOAD_PATH, LOG_PATH)

    return gnn, BATCH_SIZE


def get_acfg(fname, acfg_f_name):
    with open(acfg_f_name) as inf:
        for line in inf:
            g_info = json.loads(line.strip())
            if fname == g_info['fname']:
                return g_info['succs'], g_info['features']


def compress_graph(subg_nodes, subg_succs, features):
    node_mapping = {}  
    node_mapping_reversion = {}  
    compress_subg_succs = [] 
    compress_subg_features = []

    unique_values = list(set(subg_nodes))
    unique_values.sort()
    for i, value in enumerate(unique_values):
        node_mapping[value] = i
        node_mapping_reversion[i] = value

    for node_index in range(len(subg_succs)):
        if subg_succs[node_index] != [] or node_index in node_mapping.keys():
            compress_subg_succs.append([])
            for node in subg_succs[node_index]:
                compress_subg_succs[-1].append(node_mapping[node])

    for node_index in node_mapping_reversion.keys():
        compress_subg_features.append(features[node_mapping_reversion[node_index]])

    return compress_subg_succs, compress_subg_features

def get_g(subg, succs, features):
    g = {'node_num': 0}
    subg_succs = copy.deepcopy(succs)
    subg_nodes = []
    for i in range(len(subg['corresponding_nodes'])): 
        if subg['corresponding_nodes'][i] != -1:
            subg_nodes.append(i)
        elif subg['node_simplification_succs'][i] != -1 and subg['corresponding_nodes'][subg['node_simplification_succs'][i]] != -1: 
            subg_nodes.append(i)
        else: 
            for j in range(len(succs)):
                if i in succs[j]:
                    if i in subg_succs[j]:
                        subg_succs[j].remove(i)
            subg_succs[i] = []
    compress_subg_succs, compress_subg_features = compress_graph(subg_nodes, subg_succs, features)
    g['node_num'] = len(compress_subg_succs)
    g['succs'] = compress_subg_succs
    g['features'] = compress_subg_features

    return g                

def get_pair(g1, g2, M):
    maxN1 = g1['node_num']
    maxN2 = g2['node_num']
    feature_dim = len(g1['features'][0])
    X1_input = np.zeros((M, maxN1, feature_dim))
    X2_input = np.zeros((M, maxN2, feature_dim))
    node1_mask = np.zeros((M, maxN1, maxN1))
    node2_mask = np.zeros((M, maxN2, maxN2))

    for i in range(M):
        for u in range(g1['node_num']):
            X1_input[i, u, :] = np.array( g1['features'][u] ) 
            for v in g1['succs'][u]:
                node1_mask[i, u, v] = 1 
        for u in range(g2['node_num']):
            X2_input[i, u, :] = np.array( g2['features'][u] )
            for v in g2['succs'][u]:
                node2_mask[i, u, v] = 1

    return X1_input,X2_input,node1_mask,node2_mask