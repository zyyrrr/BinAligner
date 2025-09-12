import random
import copy

class subgraph(object):
    def __init__(self, node_num = 0):
        self.node_num = node_num 
        self.succs = [] 
        self.preds = [] 
        self.corresponding_nodes = [] 
        self.node_simp_succs = [] 
        self.node_simp_preds = [] 
        if node_num > 0:
            for i in range(node_num):
                self.succs.append([])
                self.preds.append([])
                self.corresponding_nodes.append(-1) 
                self.node_simp_succs.append(-1) 
                self.node_simp_preds.append(-1) 
                
    def add_edge(self, u, v):
        self.succs[u].append(v)
        self.preds[v].append(u)

    def is_edge_exist(self, u, v): 
        return v in self.succs[u]

    def delete_edge(self, u, v): 
        self.succs[u].remove(v)
        self.preds[v].remove(u)

    def record_corresponding_node(self, self_node, corresponding_node):
        self.corresponding_nodes[self_node] = corresponding_node

    def record_simp_node(self):
        for u in range(self.node_num):
            if len(self.succs[u]) == 1 and len(self.preds[u]) == 1:
                if self.node_simp_succs[u] != -1 and self.node_simp_preds[u] != -1:
                    continue 

                simp_path = [u] 
                v = self.succs[u][0]
                while len(self.succs[v]) == 1 and len(self.preds[v]) == 1:
                    if v not in simp_path:
                        simp_path.append(v)
                        v = self.succs[v][0]
                    else:
                        simp_path.remove(v)
                        v = self.preds[v][0]
                        simp_path.remove(v)
                        self.delete_edge(v,self.succs[v][0])
                v_succs = v

                if len(self.preds[u]):
                    v = self.preds[u][0]
                    while len(self.succs[v]) == 1 and len(self.preds[v]) == 1:
                        if v not in simp_path:
                            simp_path.append(v)
                            v = self.preds[v][0]
                        else:
                            simp_path.remove(v)
                            v = self.succs[v][0]
                            simp_path.remove(v)
                            self.delete_edge(self.preds[v][0],v)
                    v_preds = v
                else:
                    v_preds = u 

                for i in simp_path:
                    self.node_simp_succs[i] = v_succs
                    self.node_simp_preds[i] = v_preds

    def simp_cfg(self): 
        record_added_edges = [] 
        for u in range(self.node_num):
            if self.node_simp_succs[u] != -1: 
                n1 = self.node_simp_preds[u]
                n2 = self.node_simp_succs[u]
                if [n1, n2] not in record_added_edges and self.is_edge_exist(n1, n2) == False:
                    self.add_edge(n1, n2)
                    record_added_edges.append([n1, n2])
                if len(self.preds[u]) == 1: 
                    self.delete_edge(self.preds[u][0], u)
                if len(self.succs[u]) == 1: 
                    self.delete_edge(u, self.succs[u][0])

    def restore_nodes(self, origin_after_simp_preds, origin_after_simp_succs):
        for i in range(self.node_num):
            u = self.node_simp_preds[i]
            v = self.node_simp_succs[i]
            
            if self.corresponding_nodes[u] == -1 and self.corresponding_nodes[v] == -1:
                self.node_simp_preds[i] = -1
                self.node_simp_succs[i] = -1
            
            if self.corresponding_nodes[i] == -1:
                fath_has_corresponding_nodes = 0
                for u in origin_after_simp_preds[i]:
                    if self.corresponding_nodes[u] > -1:
                        fath_has_corresponding_nodes = 1
                        break
                chil_has_corresponding_nodes = 0
                for v in origin_after_simp_succs[i]:
                    if self.corresponding_nodes[v] > -1:
                        chil_has_corresponding_nodes = 1
                        break
                if fath_has_corresponding_nodes or chil_has_corresponding_nodes:
                    self.corresponding_nodes[i] = -666 
        
    def actual_corresponding_nodes(self):
        actual_corresponding_nodes = []
        for i in range(self.node_num):
            if self.corresponding_nodes[i] != -1: 
                actual_corresponding_nodes.append(i)
        return actual_corresponding_nodes
    
    def count_actual_node_num(self):
        actual_node_num = 0 
        for i in range(self.node_num):
            if self.corresponding_nodes[i] != -1: 
                actual_node_num += 1
            else: 
                if self.node_simp_succs[i] != -1: 
                    actual_node_num += 1
        return actual_node_num

    def count_actual_edge_num(self, origin_succs): 
        actual_node = [] 
        for i in range(self.node_num):
            if self.corresponding_nodes[i] != -1: 
                actual_node.append(i)
            else: 
                if self.node_simp_succs[i] != -1: 
                    actual_node.append(i)

        actual_edge_num = 0
        for u in range(len(origin_succs)):
            for v in origin_succs[u]: 
                if u in actual_node and v in actual_node: 
                    actual_edge_num += 1

        return actual_edge_num 

    def actual_nodes(self):
        actual_nodes = []
        for i in range(self.node_num):
            if self.corresponding_nodes[i] != -1: 
                actual_nodes.append(i)
            
        return actual_nodes

    def toSave(self):
        ret = {}
        ret["corresponding_nodes"] = self.corresponding_nodes
        ret["node_simp_succs"] = self.node_simp_succs
        return ret

def build_graph(g_succs):
    g = subgraph(len(g_succs))
    for u in range(len(g_succs)):
        for v in g_succs[u]:
            if u != v: 
                g.add_edge(u, v)
    g.record_simp_node()
    g.simp_cfg()
    return g

def subgraph_search(subg1, subg2, st_g1, st_g2, g1, g2):
    subg1.record_corresponding_node(st_g1, st_g2)
    subg2.record_corresponding_node(st_g2, st_g1)
    
    if (len(g1.preds[st_g1]) == 0 and len(g1.succs[st_g1]) == 0) or (len(g2.preds[st_g2]) == 0 and len(g2.succs[st_g2]) == 0):
        return

    for i in range(len(g1.preds[st_g1])-1,-1,-1):
        u = g1.preds[st_g1][i]
        st_g1_indegree = len(g1.preds[u])
        st_g1_outdegree = len(g1.succs[u])
        for j in range(len(g2.preds[st_g2])-1,-1,-1):
            v = g2.preds[st_g2][j]
            if st_g1_indegree == len(g2.preds[v]) and st_g1_outdegree == len(g2.succs[v]):
                if subg1.corresponding_nodes[u] == -1 and subg2.corresponding_nodes[v] == -1:
                    subg1.add_edge(u, st_g1)
                    g1.delete_edge(u, st_g1)
                    subg2.add_edge(v, st_g2)
                    g2.delete_edge(v, st_g2)
                    subgraph_search(subg1, subg2, u, v, g1, g2)

    for i in range(len(g1.succs[st_g1])-1,-1,-1):
        u = g1.succs[st_g1][i]
        st_g1_indegree = len(g1.preds[u])
        st_g1_outdegree = len(g1.succs[u])
        for j in range(len(g2.succs[st_g2])-1,-1,-1):
            v = g2.succs[st_g2][j]
            if st_g1_indegree == len(g2.preds[v]) and st_g1_outdegree == len(g2.succs[v]):
                if subg1.corresponding_nodes[u] == -1 and subg2.corresponding_nodes[v] == -1:
                    subg1.add_edge(st_g1, u)
                    g1.delete_edge(st_g1, u)
                    subg2.add_edge(st_g2, v)
                    g2.delete_edge(st_g2, v)
                    subgraph_search(subg1, subg2, u, v, g1, g2)

def get_cur_max_subgraph(g1, g2, st_g1, st_g2, g1_succs, g2_succs, max_subg1, max_subg2):
    cur_subg1 = subgraph(g1.node_num)
    cur_subg1.node_simp_succs = copy.deepcopy(g1.node_simp_succs)
    cur_subg1.node_simp_preds = copy.deepcopy(g1.node_simp_preds)
    cur_subg2 = subgraph(g2.node_num)
    cur_subg2.node_simp_succs = copy.deepcopy(g2.node_simp_succs)
    cur_subg2.node_simp_preds = copy.deepcopy(g2.node_simp_preds)
    subgraph_search(cur_subg1, cur_subg2, st_g1, st_g2, build_graph(g1_succs), build_graph(g2_succs))
    
    cur_subg1.restore_nodes(g1.preds, g1.succs)
    cur_subg2.restore_nodes(g2.preds, g2.succs)
    if max_subg1 == '':
        max_subg1 = cur_subg1
        max_subg2 = cur_subg2
    else: 
        cur_max_node_num = max_subg1.count_actual_node_num() + max_subg2.count_actual_node_num()
        cur_node_num = cur_subg1.count_actual_node_num() + cur_subg2.count_actual_node_num()
        if cur_max_node_num < cur_node_num:
            max_subg1 = cur_subg1
            max_subg2 = cur_subg2 
        elif cur_max_node_num == cur_node_num:
            cur_max_edge_num = max_subg1.count_actual_edge_num(g1_succs) + max_subg2.count_actual_edge_num(g2_succs)
            cur_edge_num = cur_subg1.count_actual_edge_num(g1_succs) + cur_subg2.count_actual_edge_num(g2_succs)
            if cur_max_edge_num < cur_edge_num:
                max_subg1 = cur_subg1
                max_subg2 = cur_subg2  

    return max_subg1, max_subg2

def random_search(g1_succs, g2_succs):
    g1 = build_graph(g1_succs)
    g2 = build_graph(g2_succs)
    
    if g1.node_num == 1:
        g1.record_corresponding_node(0, 0)
        g2.record_corresponding_node(0, 0)
        if g2.node_num > 1:
            if g2.node_simp_preds[0] != -1:
                g2.corresponding_nodes[g2.node_simp_preds[0]] = -666 
                g2.corresponding_nodes[g2.node_simp_succs[0]] = -666 
                for i in range(1, g2.node_num):
                    if g2.node_simp_preds[i] != g2.node_simp_preds[0] or g2.node_simp_succs[i] != g2.node_simp_succs[0]:
                        g2.node_simp_preds[i] = -1
                        g2.node_simp_succs[i] = -1
            else:
                g2.restore_nodes(g2.preds, g2.succs)
        return [g1], [g2]

    subg1s = []
    subg2s = []
    random.seed(0)
    random_order = list(range(0, g1.node_num))
    random.shuffle(random_order) 
    g1_nodes_flag = copy.deepcopy(random_order)
    g2_nodes_flag = list(range(0, g2.node_num)) 
    for st_g1 in random_order:
        if g1.node_simp_succs[st_g1] != -1: 
            continue
        if st_g1 not in g1_nodes_flag: 
            continue
        max_subg1 = '' 
        max_subg2 = ''
        st_g1_indegree = len(g1.preds[st_g1])
        st_g1_outdegree = len(g1.succs[st_g1])
        for st_g2 in range(g2.node_num):
            if st_g1_indegree == len(g2.preds[st_g2]) and st_g1_outdegree == len(g2.succs[st_g2]):
                max_subg1, max_subg2 = get_cur_max_subgraph(g1, g2, st_g1, st_g2, g1_succs, g2_succs, max_subg1, max_subg2)    
        if max_subg1 != '':
            subg1s.append(max_subg1)
            subg2s.append(max_subg2)
            g1_nodes_flag = list(set(g1_nodes_flag) - set(max_subg1.actual_nodes())) 
            g2_nodes_flag = list(set(g2_nodes_flag) - set(max_subg2.actual_nodes()))

    if len(g2_nodes_flag): 
        for st_g2 in range(g2.node_num):
            if g2.node_simp_succs[st_g2] != -1: 
                continue
            if st_g2 not in g2_nodes_flag: 
                continue
            max_subg1 = '' 
            max_subg2 = ''
            st_g2_indegree = len(g2.preds[st_g2])
            st_g2_outdegree = len(g2.succs[st_g2])
            for st_g1 in range(g1.node_num):
                if st_g2_indegree == len(g1.preds[st_g1]) and st_g2_outdegree == len(g1.succs[st_g1]):
                    max_subg1, max_subg2 = get_cur_max_subgraph(g1, g2, st_g1, st_g2, g1_succs, g2_succs, max_subg1, max_subg2)
            if max_subg1 != '':
                subg1s.append(max_subg1)
                subg2s.append(max_subg2)  
                g2_nodes_flag = list(set(g2_nodes_flag) - set(max_subg2.actual_nodes()))               

    return subg1s, subg2s

def find_candidate_subgraph_pairs(g1_succs, g2_succs): 
    search_times = 1 
    if len(g1_succs) <= len(g2_succs):
        for i in range(search_times):
            candidate_subgraph_pairs_in_g1, candidate_subgraph_pairs_in_g2 = random_search(g1_succs, g2_succs)
    else:
        for i in range(search_times):
            candidate_subgraph_pairs_in_g2, candidate_subgraph_pairs_in_g1 = random_search(g2_succs, g1_succs)

    if candidate_subgraph_pairs_in_g1 == []: 
        return None, None
    
    return candidate_subgraph_pairs_in_g1, candidate_subgraph_pairs_in_g2