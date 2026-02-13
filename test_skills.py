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