# Architecture Documentation

## Overview

This project implements a skills exploration tool that analyzes O*NET occupational data to identify relationships between workplace skills. The system builds a network graph representation of skills, applies community detection algorithms to identify natural skill clusters, and provides visualization and analysis capabilities.

## System Components

The system consists of three main components organized in `skills.py`:

### 1. Graph Construction (`build_skills_graph`)
**Purpose:** Transforms raw O*NET Excel data into a NetworkX graph representation

**Input:** Path to Skills.xlsx file containing O*NET skill ratings by occupation

**Processing:**
- Filters skills with importance ratings > 2.5 (Scale ID = 'IM')
- Groups data by occupation (O*NET-SOC Code)
- Creates nodes for each skill with metadata (Element ID, Element Name, occupations list)
- Creates weighted edges between skills that co-occur in the same occupation
- Edge weights represent the number of occupations where two skills appear together

**Output:** NetworkX Graph object with 35 skill nodes and weighted edges

### 2. Community Detection (`community_detection`, `get_skills_by_community`)
**Purpose:** Identifies natural clusters of related skills using graph algorithms

**Algorithm:** Louvain method for community detection (via `nx.community.louvain_communities`)
- Optimizes modularity to find densely connected skill groups
- Configurable resolution parameter controls granularity
- Typical results: 2 major communities (cognitive/communication vs. technical/operational)

**Data Flow:**
1. `community_detection()` receives skills graph
2. Applies Louvain algorithm with resolution parameter
3. Returns dictionary mapping skill IDs to community IDs
4. `get_skills_by_community()` reorganizes this mapping into human-readable format
5. Groups skills by community with (skill_id, skill_label) tuples for display

**Output:** Dictionary structure enabling queries like "show all skills in community 0"

### 3. Visualization (`visualize_communities`)
**Purpose:** Creates publication-quality network visualizations showing community structure

**Rendering Strategy:**
- Spring layout algorithm positions nodes to separate communities visually
- Distinct colors for each community (matplotlib Set3 colormap)
- Selective labeling: only top 5 most-connected skills per community (prevents visual clutter)
- High-resolution output (300 dpi) suitable for presentations and papers

**Output:** PNG image file showing network structure with color-coded communities

## Data Flow Architecture
```
Skills.xlsx (O*NET Data)
        ↓
build_skills_graph()
        ↓
NetworkX Graph (35 nodes, weighted edges)
        ↓
community_detection()
        ↓
Skill-to-Community Mapping (dict)
        ↓
    ↙              ↘
get_skills_by_community()    visualize_communities()
    ↓                              ↓
Community Organization      Network Visualization PNG
```

## Key Design Decisions

### Why NetworkX?
NetworkX provides robust graph algorithms including community detection methods validated in published research. The Louvain algorithm implementation is well-tested and matches the methodology used in the Alabdulkareem et al. (2018) reference paper on skill polarization.

### Why Importance Threshold of 2.5?
O*NET rates skill importance on a 1-5 scale. Using > 2.5 filters for skills that are genuinely important to an occupation, reducing noise from marginal skill requirements. This threshold balances graph size with meaningful connections.

### Why Weighted Edges?
Edge weights represent how many occupations require both skills. Higher weights indicate skills that frequently co-occur, strengthening community detection accuracy. For example, "Active Listening" and "Speaking" have high edge weight because most communication-intensive jobs require both.

### Why Spring Layout for Visualization?
Spring layout (force-directed graph drawing) naturally separates clusters while keeping connected nodes close. This makes community structure visually obvious without manual positioning. The `k=0.5` parameter provides optimal spacing for typical skill network density.

## Integration Points

### Streamlit Interface (`app.py`)
The Streamlit web interface imports these functions to provide interactive skill exploration:
- User selects a skill via dropdown
- System displays related skills and their shared occupations
- Future enhancement: Display community membership and visualizations

### Testing (`test_skills.py`)
Unit tests verify each component's behavior:
- Graph construction tests ensure correct node/edge creation
- Community detection tests verify all skills get assigned to communities
- Visualization tests confirm output files are created successfully

## Dependencies

**Core Libraries:**
- `pandas`: Excel file parsing and data manipulation
- `networkx`: Graph construction and community detection algorithms
- `matplotlib`: Network visualization and PNG generation
- `openpyxl`: Excel file format support (pandas backend)

**Python Version:** 3.9+ (tested on 3.9.7, 3.12)

## Performance Characteristics

**Graph Construction:** O(n²) where n = number of skills per occupation
- Typical runtime: <1 second for full O*NET dataset (35 skills, ~1000 occupations)

**Community Detection:** O(m log n) where m = edges, n = nodes (Louvain algorithm)
- Typical runtime: <0.5 seconds for skill network

**Visualization:** O(n + m) for layout calculation
- Typical runtime: 1-2 seconds including PNG rendering

**Total Pipeline:** ~3-4 seconds for complete analysis and visualization

## Future Architecture Considerations

**Potential Enhancements:**
1. **Caching:** Cache graph construction results to avoid re-parsing Excel on every run
2. **Alternative Algorithms:** Compare Louvain with other community detection methods (Girvan-Newman, Label Propagation)
3. **Interactive Visualization:** Replace static PNG with interactive plots (Plotly, Bokeh)
4. **Hierarchical Communities:** Detect nested community structure at multiple resolutions
5. **Temporal Analysis:** Track how skill communities change across O*NET versions

## References

This architecture implements methods from:

Alabdulkareem, A., Frank, M. R., Sun, L., AlShebli, B., Hidalgo, C., & Rahwan, I. (2018). Unpacking the polarization of workplace skills. *Science Advances*, 4(7), eaao6030. https://doi.org/10.1126/sciadv.aao6030

The Louvain community detection algorithm:

Blondel, V. D., Guillaume, J. L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*, 2008(10), P10008.


