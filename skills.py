import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def add_occupation(skills_graph, node_id, row):
    if (row['Title'], row['Data Value']) not in skills_graph.nodes[node_id]['occupations']:
        skills_graph.nodes[node_id]['occupations'].append((row['Title'], row['Data Value']))

def add_neighbor(skills_graph, group, neighbor_idx, current_node, row):
    neighbor_node = group.iloc[neighbor_idx]['Element ID']
    # we dont' want loops to self
    if current_node == neighbor_node:
        return

    if not skills_graph.has_node(neighbor_node):
        skills_graph.add_node(neighbor_node, label=group.iloc[neighbor_idx]['Element Name'], occupations=[])
        
    add_occupation(skills_graph, neighbor_node, row)

    if not skills_graph.has_edge(current_node, neighbor_node):
        skills_graph.add_edge(current_node, neighbor_node)
        skills_graph[current_node][neighbor_node]["weight"] = 0

    skills_graph[current_node][neighbor_node]["weight"] = skills_graph[current_node][neighbor_node]["weight"] + 1

def build_skills_graph(path_to_skills):
    df = pd.read_excel(path_to_skills)

    # only use skills with importance greater than 2.5
    filtered_df = df[df['Scale ID'] == 'IM'][df['Data Value'] > 2.5]
    filtered_df = filtered_df.reset_index()
    
    # group data by O*NET-SOC Code so we can then iterate over each skill in each occupation
    grouped_df = filtered_df.groupby('O*NET-SOC Code')

    skills_graph = nx.Graph()

    for code, group in grouped_df:
        # iterate over all groups (one group represents one occupation)
        index = 0
        for row_idx, row in group.iterrows():
            # iterate over all skills in an occupation
            # and add an edge between skills in the same occupation if it doesn't exist
            # increase weight for every additional time two skills belong to the same occupation
            current_node = row['Element ID']
            if not skills_graph.has_node(current_node):
                skills_graph.add_node(current_node, label=row['Element Name'], occupations=[])
                
            add_occupation(skills_graph, current_node, row)

            for neighbor_idx in range(index+1, group.count()['index']):
                add_neighbor(skills_graph, group, neighbor_idx, current_node, row)

            index = index+1
    return skills_graph
    

skills_graph = build_skills_graph("data/Skills.xlsx")
selected_skill = input("Enter the code of a skill: ")
edges = skills_graph.edges(selected_skill, data=True)
edges = sorted(edges, reverse=True, key=lambda edge: edge[2].get('weight', 1))
#resolution parameter to be finalized (issue 15)
communities = nx.community.louvain_communities(skills_graph, resolution=1.2)

print(f'\nNumber of communities: {len(communities)}') # ==16
print("\n")

print(f'\nOften used skills with "{skills_graph.nodes[selected_skill]['label']} ({selected_skill})":')
occupations_selected = skills_graph.nodes[selected_skill]["occupations"]
for edge in edges[:10]:
    occupations = skills_graph.nodes[edge[1]]['occupations']
    intersection = sorted(list(set(occupations_selected) & set(occupations)), reverse=True, key=lambda prof: prof[1])
    print(f'"{skills_graph.nodes[edge[1]]['label']} ({edge[1]})" e.g. as {", ".join([f'{occup[0]} ({occup[1]})' for occup in intersection[:5]])}')
    print("\n")


