# Skills Exploration Tool with Community Detection

## Description
This project enhances the CAS502 Skills Exploration Tool starter project by adding community detection to identify natural clusters of skills in the labor market data. The starter tool creates a weighted network graph from O*NET occupational skills data and allows users to query which skills are most often used together, but users don’t gain a higher-level understanding of whether those skills form a coherent “community” or how their chosen skills fit into the landscape when organized into these communities. Our enhancement uses NetworkX's built-in Louvain community detection algorithm to reveal emergent skill groupings (e.g., management skills, technical skills, creative skills forming distinct clusters) rather than isolated pairwise connections. This adds approximately 20-40 lines of new code while demonstrating complex systems concepts.

## Project Team
Logan Emerson (@logemerson)
George Estrada (@OrionDS2026)

## Features

### Community Detection
The project implements three core functions for analyzing skill communities:

1. **`community_detection(skills_graph, resolution=1.0)`**
   - Applies the Louvain algorithm to detect natural skill clusters
   - Returns a dictionary mapping skill IDs to community IDs
   - Configurable resolution parameter controls cluster granularity

2. **`get_skills_by_community(skill_to_community_map, skills_graph)`**
   - Organizes skills by their detected communities
   - Returns human-readable skill labels grouped by community ID
   - Enables queries like "show all skills in community 0"

3. **`visualize_communities(skills_graph, skill_to_community_map, output_file)`**
   - Generates network visualizations with nodes colored by community
   - Uses spring layout to visually separate skill clusters
   - Labels the most connected skills in each community
   - Outputs high-resolution PNG images (300 dpi)

### Typical Results
Analysis of the O*NET skills data typically reveals 2 major communities:
- **Community 0 (Cognitive/Communication):** Active Listening, Speaking, Reading Comprehension, Writing, Mathematics
- **Community 1 (Technical/Operational):** Equipment Selection, Operations Monitoring, Equipment Maintenance, Operation and Control, Troubleshooting

This clustering validates the skill polarization patterns identified in published research (Alabdulkareem et al., 2018).

## Installation

### Requirements
Install dependencies via [requirements.txt](requirements.txt).
- Python 3.9+
- pandas
- networkx
- matplotlib
- openpyxl

### Setup
#### Clone the repository
```bash
git clone https://github.com/logemerson/CAS502-skills-exploration-communities.git
cd CAS502-skills-exploration-communities
```
## Usage

### Basic Usage
```python
from skills import build_skills_graph, community_detection, get_skills_by_community, visualize_communities

# Build the skills network from O*NET data
graph = build_skills_graph('data/Skills.xlsx')

# Detect communities
communities_map = community_detection(graph)

# Organize skills by community
communities = get_skills_by_community(communities_map, graph)

# Print skills in each community
for community_id, skills in communities.items():
    print(f"\nCommunity {community_id}:")
    for skill_id, skill_name in skills[:5]:  # Show first 5
        print(f"  - {skill_name} ({skill_id})")

# Generate visualization
visualize_communities(graph, communities_map, 'output.png')
```

### Running Tests
```bash
python -m unittest test_skills.py -v
```

All 16 unit tests should pass, covering graph construction, community detection, and visualization functions.

## Technical Documentation

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Contributing

We welcome contributions! If you'd like to contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Make your changes and commit them with descriptive messages
4. Add tests for any new functionality
5. Ensure all tests pass (`python -m unittest test_skills.py -v`)
6. Push to your fork and submit a pull request

Please follow the existing code style and include appropriate documentation for any new features.

## Bug Reports and Feature Requests

If you encounter bugs or have feature requests:

1. Check the [Issues](https://github.com/logemerson/CAS502-skills-exploration-communities/issues) page to see if it's already reported
2. If not, create a new issue with:
   - A clear, descriptive title
   - Detailed description of the bug or feature request
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior (for bugs)
   - Your Python version and operating system

## References

Alabdulkareem, A., Frank, M. R., Sun, L., AlShebli, B., Hidalgo, C., & Rahwan, I. (2018). Unpacking the polarization of workplace skills. *Science Advances*, 4(7), eaao6030. https://doi.org/10.1126/sciadv.aao6030
