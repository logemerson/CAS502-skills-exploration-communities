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
    
def community_detection(skills_graph, resolution=1.0):
    """
    Detect communities in the skills graph using the Louvain algorithm.
    
    Args:
        skills_graph: NetworkX graph object containing skills and their connections
        resolution: Resolution parameter for the Louvain algorithm (default 1.0)
                   Higher values create more communities, lower values create fewer
    
    Returns:
        Dictionary mapping skill IDs to their community ID
        Example: {'2.A.1.a': 0, '2.A.1.b': 0, '2.B.1.a': 1}
    """
    communities = nx.community.louvain_communities(skills_graph, resolution=resolution)
    
    # Convert from list of sets to dictionary mapping skill -> community_id
    skill_to_community = {}
    for community_id, community in enumerate(communities):
        for skill in community:
            skill_to_community[skill] = community_id
    
    return skill_to_community

def get_skills_by_community(skill_to_community_map, skills_graph):
    """
    Organize skills by their community assignments with readable labels.
    
    Args:
        skill_to_community_map: Dictionary mapping skill IDs to community IDs
                               (output from community_detection function)
        skills_graph: NetworkX graph object containing skill labels
    
    Returns:
        Dictionary where keys are community IDs and values are lists of 
        (skill_id, skill_label) tuples
        
        Example: {
            0: [('2.A.1.a', 'Reading Comprehension'), ('2.A.1.b', 'Active Listening')],
            1: [('2.C.1.a', 'Time Management'), ('2.C.1.b', 'Coordination')]
        }
    """
    communities = {}
    
    for skill_id, community_id in skill_to_community_map.items():
        if community_id not in communities:
            communities[community_id] = []
        
        skill_label = skills_graph.nodes[skill_id].get('label', skill_id)
        communities[community_id].append((skill_id, skill_label))
    
    # Sort skills within each community by ID for consistency
    for community_id in communities:
        communities[community_id].sort(key=lambda x: x[0])
    
    return communities

def visualize_communities(skills_graph, skill_to_community_map, output_file='community_graph.png'):
    """
    Create a visualization of the skills network with nodes colored by community.
    
    Args:
        skills_graph: NetworkX graph object containing skills and connections
        skill_to_community_map: Dictionary mapping skill IDs to community IDs
        output_file: Filename to save the visualization (default: 'community_graph.png')
    
    Returns:
        Path to the saved visualization file
    """
    # Create a color map for nodes based on their community
    communities = set(skill_to_community_map.values())
    colors = plt.cm.Set3(range(len(communities)))  # Use Set3 colormap for distinct colors
    
    node_colors = []
    for node in skills_graph.nodes():
        community_id = skill_to_community_map.get(node, 0)
        node_colors.append(colors[community_id])
    
    # Create the visualization
    plt.figure(figsize=(16, 12))
    
    # Use spring layout for better separation of communities
    pos = nx.spring_layout(skills_graph, k=0.5, iterations=50, seed=42)
    
    # Draw the graph
    nx.draw_networkx_nodes(skills_graph, pos, node_color=node_colors, 
                          node_size=100, alpha=0.8)
    nx.draw_networkx_edges(skills_graph, pos, alpha=0.2, width=0.5)
    
    # Add labels for a subset of nodes (to avoid clutter)
    # Label the 10 most connected nodes in each community
    labels_to_show = {}
    communities_dict = get_skills_by_community(skill_to_community_map, skills_graph)
    
    for community_id, skills in communities_dict.items():
        # Get node degrees for skills in this community
        skill_degrees = [(skill_id, skills_graph.degree(skill_id)) for skill_id, _ in skills]
        # Sort by degree and take top 5
        top_skills = sorted(skill_degrees, key=lambda x: x[1], reverse=True)[:5]
        for skill_id, _ in top_skills:
            labels_to_show[skill_id] = skills_graph.nodes[skill_id]['label']
    
    nx.draw_networkx_labels(skills_graph, pos, labels_to_show, font_size=8)
    
    plt.title(f'Skills Network - {len(communities)} Communities Detected', fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualization saved to {output_file}")
    return output_file        

if __name__ == "__main__":
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


