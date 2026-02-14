import unittest
import skills

class TestAddOccupation(unittest.TestCase):

    def test_add_occupation_adds_new_occupation(self):
        # Create a simple test graph with one node
        import networkx as nx
        test_graph = nx.Graph()
        test_graph.add_node('SK001', label='Test Skill', occupations=[])
        
        # Create a mock row (simulating Excel data)
        test_row = {'Title': 'Software Developer', 'Data Value': 4.5}
        
        # Call the function we're testing
        skills.add_occupation(test_graph, 'SK001', test_row)
        
        # Check that the occupation was added
        self.assertEqual(len(test_graph.nodes['SK001']['occupations']), 1)
        self.assertIn(('Software Developer', 4.5), test_graph.nodes['SK001']['occupations'])

    def test_add_occupation_prevents_duplicates(self):
        # Create a test graph with a node that already has an occupation
        import networkx as nx
        test_graph = nx.Graph()
        test_graph.add_node('SK002', label='Another Skill', occupations=[('Data Analyst', 3.8)])
        
        # Try to add the same occupation again
        test_row = {'Title': 'Data Analyst', 'Data Value': 3.8}
        skills.add_occupation(test_graph, 'SK002', test_row)
        
        # Check that it still only has ONE occupation (no duplicate)
        self.assertEqual(len(test_graph.nodes['SK002']['occupations']), 1)

    def test_add_occupation_adds_multiple_different_occupations(self):
        # Start with a node that has no occupations
        import networkx as nx
        test_graph = nx.Graph()
        test_graph.add_node('SK003', label='Test Skill', occupations=[])
        
        # Add three different occupations
        test_row1 = {'Title': 'Nurse', 'Data Value': 4.0}
        test_row2 = {'Title': 'Doctor', 'Data Value': 4.5}
        test_row3 = {'Title': 'Pharmacist', 'Data Value': 3.5}
        
        skills.add_occupation(test_graph, 'SK003', test_row1)
        skills.add_occupation(test_graph, 'SK003', test_row2)
        skills.add_occupation(test_graph, 'SK003', test_row3)
        
        # Check that all three were added
        self.assertEqual(len(test_graph.nodes['SK003']['occupations']), 3)


class TestBuildSkillsGraph(unittest.TestCase):
    
    def test_build_skills_graph_creates_graph(self):
        # Create a minimal test Excel file with just a few rows
        import pandas as pd
        import tempfile
        import os
        
        # Create test data that mimics the Skills.xlsx structure
        test_data = {
            'O*NET-SOC Code': ['11-1011.00', '11-1011.00', '11-2021.00'],
            'Element ID': ['2.A.1.a', '2.A.1.b', '2.A.1.a'],
            'Element Name': ['Reading Comprehension', 'Active Listening', 'Reading Comprehension'],
            'Scale ID': ['IM', 'IM', 'IM'],
            'Data Value': [3.5, 3.0, 4.0],
            'Title': ['CEO', 'CEO', 'Marketing Manager']
        }
        df = pd.DataFrame(test_data)
        
        # Save to a temporary Excel file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as tmp_file:
            temp_path = tmp_file.name
            df.to_excel(temp_path, index=False)
        
        try:
            # Call the function with our test file
            graph = skills.build_skills_graph(temp_path)
            
            # Test that a graph was created
            self.assertIsNotNone(graph)
            
            # Test that the graph has nodes
            self.assertGreater(len(graph.nodes), 0)
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    def test_build_skills_graph_creates_correct_nodes(self):
        # Create test data with known skills
        import pandas as pd
        import tempfile
        import os
        
        test_data = {
            'O*NET-SOC Code': ['11-1011.00', '11-1011.00'],
            'Element ID': ['2.A.1.a', '2.A.1.b'],
            'Element Name': ['Reading Comprehension', 'Active Listening'],
            'Scale ID': ['IM', 'IM'],
            'Data Value': [3.5, 3.0],
            'Title': ['CEO', 'CEO']
        }
        df = pd.DataFrame(test_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as tmp_file:
            temp_path = tmp_file.name
            df.to_excel(temp_path, index=False)
        
        try:
            graph = skills.build_skills_graph(temp_path)
            
            # Check that specific nodes were created
            self.assertIn('2.A.1.a', graph.nodes)
            self.assertIn('2.A.1.b', graph.nodes)
            
            # Check that nodes have the correct labels
            self.assertEqual(graph.nodes['2.A.1.a']['label'], 'Reading Comprehension')
            
        finally:
            os.unlink(temp_path)

    def test_build_skills_graph_creates_edges(self):
        # Create test data where two skills appear in the same occupation
        import pandas as pd
        import tempfile
        import os
        
        test_data = {
            'O*NET-SOC Code': ['11-1011.00', '11-1011.00'],
            'Element ID': ['2.A.1.a', '2.A.1.b'],
            'Element Name': ['Reading Comprehension', 'Active Listening'],
            'Scale ID': ['IM', 'IM'],
            'Data Value': [3.5, 3.0],
            'Title': ['CEO', 'CEO']
        }
        df = pd.DataFrame(test_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as tmp_file:
            temp_path = tmp_file.name
            df.to_excel(temp_path, index=False)
        
        try:
            graph = skills.build_skills_graph(temp_path)
            
            # Check that an edge exists between the two skills (they're in the same occupation)
            self.assertTrue(graph.has_edge('2.A.1.a', '2.A.1.b'))
            
            # Check that the edge has a weight
            self.assertIn('weight', graph['2.A.1.a']['2.A.1.b'])
            
        finally:
            os.unlink(temp_path)

                                