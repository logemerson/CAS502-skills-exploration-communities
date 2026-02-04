import pandas as pd
import networkx as nx
import streamlit as st

# ============================================================
# GRAPH BUILDING FUNCTIONS (from original skills.py)
# ============================================================

def add_occupation(skills_graph, node_id, row):
    """Add an occupation to a skill node's list of occupations."""
    if (row['Title'], row['Data Value']) not in skills_graph.nodes[node_id]['occupations']:
        skills_graph.nodes[node_id]['occupations'].append((row['Title'], row['Data Value']))


def add_neighbor(skills_graph, group, neighbor_idx, current_node, row):
    """Add a neighboring skill node and create/update the edge between them."""
    neighbor_node = group.iloc[neighbor_idx]['Element ID']
    
    # We don't want loops to self
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
    """
    Build a weighted graph of skills from O*NET data.
    
    Nodes: Skills (identified by Element ID like '2.A.1.a')
    Edges: Connect skills that appear together in occupations
    Edge weights: Number of occupations where both skills appear
    """
    df = pd.read_excel(path_to_skills)

    # Only use skills with importance greater than 2.5
    filtered_df = df[(df['Scale ID'] == 'IM') & (df['Data Value'] > 2.5)]
    filtered_df = filtered_df.reset_index()
    
    # Group data by O*NET-SOC Code so we can iterate over each skill in each occupation
    grouped_df = filtered_df.groupby('O*NET-SOC Code')

    skills_graph = nx.Graph()

    for code, group in grouped_df:
        index = 0
        for row_idx, row in group.iterrows():
            current_node = row['Element ID']
            if not skills_graph.has_node(current_node):
                skills_graph.add_node(current_node, label=row['Element Name'], occupations=[])
                
            add_occupation(skills_graph, current_node, row)

            for neighbor_idx in range(index+1, group.count()['index']):
                add_neighbor(skills_graph, group, neighbor_idx, current_node, row)

            index = index+1
    
    return skills_graph


# ============================================================
# STREAMLIT APP
# ============================================================

# Page configuration
st.set_page_config(
    page_title="Skills Exploration Tool",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 Skills Exploration Tool")
st.markdown("""
This tool analyzes O*NET occupational data to show which skills are most often used together 
across different professions. Select a skill to discover related skills and example occupations.
""")

# Load the graph (cached so it only builds once)
@st.cache_data
def load_graph():
    return build_skills_graph("data/Skills.xlsx")

# Show loading message while building graph
with st.spinner("Building skills network from O*NET data... (this takes a moment the first time)"):
    skills_graph = load_graph()

# Create a dictionary mapping skill names to codes for the dropdown
skill_options = {
    f"{skills_graph.nodes[node]['label']} ({node})": node 
    for node in skills_graph.nodes()
}

# Sort by skill name for easier browsing
skill_options_sorted = dict(sorted(skill_options.items()))

# Sidebar for skill selection
st.sidebar.header("Select a Skill")
selected_display = st.sidebar.selectbox(
    "Choose a skill to analyze:",
    options=list(skill_options_sorted.keys()),
    index=0
)

# Get the skill code from the selection
selected_skill = skill_options_sorted[selected_display]

# Display results
st.header(f"Analysis: {skills_graph.nodes[selected_skill]['label']}")
st.caption(f"Skill Code: {selected_skill}")

# Get and sort edges by weight
edges = skills_graph.edges(selected_skill, data=True)
edges = sorted(edges, reverse=True, key=lambda edge: edge[2].get('weight', 1))

# Get occupations for selected skill
occupations_selected = skills_graph.nodes[selected_skill]["occupations"]

st.subheader("🔗 Top 10 Related Skills")
st.markdown("These skills most frequently appear together with the selected skill across occupations:")

# Display related skills in a cleaner format
for i, edge in enumerate(edges[:10], 1):
    related_skill_code = edge[1]
    related_skill_name = skills_graph.nodes[related_skill_code]['label']
    connection_strength = edge[2].get('weight', 1)
    
    # Find overlapping occupations
    occupations = skills_graph.nodes[related_skill_code]['occupations']
    intersection = sorted(
        list(set(occupations_selected) & set(occupations)), 
        reverse=True, 
        key=lambda prof: prof[1]
    )
    
    # Create an expander for each related skill
    with st.expander(f"**{i}. {related_skill_name}** (Connection strength: {connection_strength})"):
        st.write(f"**Skill Code:** {related_skill_code}")
        st.write(f"**Shared Occupations:** {len(intersection)}")
        
        if intersection:
            st.write("**Example occupations where both skills are important:**")
            # Create a small table of example occupations
            examples = intersection[:5]
            example_df = pd.DataFrame(examples, columns=["Occupation", "Importance Score"])
            st.table(example_df)

# Stats in the sidebar
st.sidebar.markdown("---")
st.sidebar.header("📊 Network Statistics")
st.sidebar.metric("Total Skills in Network", skills_graph.number_of_nodes())
st.sidebar.metric("Total Connections", skills_graph.number_of_edges())
st.sidebar.metric("Occupations for Selected Skill", len(occupations_selected))

# Footer
st.markdown("---")
st.caption("Data source: O*NET Database v29.1 | Built for CAS502 at Arizona State University")
