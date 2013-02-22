import random
import sympy as sp
import unittest

from GraphManager import GraphManager
from GraphExceptions import SolverException, ConfigurationException
from GraphVariable import GraphVariable
from GraphGenetics import GenomeBase, Population


class TestPopulation(unittest.TestCase):

    def test_population_graph_manager_is_graph_manager(self):
        with self.assertRaises(ConfigurationException):
            p = Population(None)

    def test_population_default_settings(self):
        gm = GraphManager()
        p = Population(gm)
        self.assertEqual(p.settings['size'], 40)
        self.assertEqual(p.settings['iterations'], 1000)
        self.assertEqual(p.settings['permutation_chance'], 0.05)
        self.assertEqual(p.settings['crossover_chance'], 0.05)
        self.assertEqual(p.settings['fitness_var'], 'fitness')

    def test_population_update_setting(self):
        gm = GraphManager()
        p = Population(gm)
        self.assertEqual(p.settings['size'], 40)
        
        p.setting('size', 50)
        self.assertEqual(p.settings['size'], 50)

    def test_generate_population(self):
        json = ""
        with open('test_data/genetic_basic.json','r') as f:
            json = f.read()
        gm = GraphManager()
        gm.load_json(json)
        p = Population(gm)
        p.generate()

        # check that a population was generated
        self.assertEqual(len(p._objects), 40)
        
        # check each member is a GenomBase
        for o in p._objects:
            self.assertIs(type(o), GenomeBase)


class TestGenome(unittest.TestCase):

    def test_initialise_default_lists_no_labels(self):
        gb = GenomeBase()
        self.assertEqual(gb.genome_length(), 10)
        gl = gb.genome_list()
        for g in gl.keys():
            self.assertLessEqual(gl[g], 9)
            self.assertGreaterEqual(gl[g], 0)

    def test_initialise_lists_with_parameters_no_labels(self):
        gb = GenomeBase(num=5, min=0, max=3)
        self.assertEqual(gb.genome_length(), 5)
        gl = gb.genome_list()
        for g in gl.keys():
            self.assertLessEqual(gl[g], 9)
            self.assertGreaterEqual(gl[g], 0)

    def test_initialise_default_lists_with_labels(self):
        labels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        gb = GenomeBase()
        self.assertEqual(gb.genome_length(), 10)
        gl = gb.genome_list()
        for g in gl.keys():
            self.assertIn(g, labels)
            self.assertLessEqual(gl[g], 9)
            self.assertGreaterEqual(gl[g], 0)

    def test_initialise_lists_with_parameters_with_labels(self):
        labels = ["a","b","c","d","e"]
        gb = GenomeBase(num=5, min=0, max=3, labels=labels)
        self.assertEqual(gb.genome_length(), 5)
        gl = gb.genome_list()
        for g in gl.keys():
            self.assertIn(g, labels)
            self.assertLessEqual(gl[g], 9)
            self.assertGreaterEqual(gl[g], 0)

    def test_load_parameters_from_graph_manager(self):
        # build the GraphManager structure from file
        json = ""
        with open('test_data/genetic_basic.json', 'r') as f:
            json = f.read()
        gm = GraphManager()
        gm.load_json(json)

        # create a genome base from the graph manager use defaults
        gb = GenomeBase(graph_manager=gm)

        # get the required values
        gl_len = gb.genome_length()
        gl = gb.genome_list()
        gl_keys = sorted(gl.keys())

        # check our length and labels were correctly applied
        self.assertEqual(3, gl_len)
        self.assertEqual(['a','b','c'], gl_keys)

    def test_incorrect_label_list_length_raises_configuration_exception(self):
        labels=[1,2,3]
        with self.assertRaises(ConfigurationException):
            gb = GenomeBase(num=5, min=0, max=3, labels=labels)

    def test_calculate_fitness_no_graph_manager(self):
        gb = GenomeBase(num=5, min=0, max=3)
        gl = gb.genome_list()
        
        # calculate fitness
        fitness = 0
        for g in gl.keys():
            fitness += gl[g]

        # check our fitness was correctly calculated
        self.assertEqual(gb.fitness(), fitness)

    def test_calculate_fitness(self):
        # build the GraphManager structure from file
        json = ""
        with open('test_data/genetic_basic.json', 'r') as f:
            json = f.read()
        gm = GraphManager()
        gm.load_json(json)
        
        # hand it to a genome
        gb = GenomeBase(gm, 3, 0, 9)
        
        # get the genome list
        gl = gb.genome_list()
        
        # calculate fitness: 30 - (a+b+c)
        fitness = 30
        for g in gl.keys():
            fitness -= gl[g]
        
        # check fitness mathces
        self.assertEqual(gb.fitness(), fitness)

    def test_random_mutation(self):
        gb = GenomeBase()
        gb2 = GenomeBase(num=20)
        self.assertEqual(gb.mutate(specific_seed=1), 1)
        self.assertEqual(gb2.mutate(specific_seed=1), 3)
        
        # brute force test no specific seed - 1000 times
        for i in range(0,1000):
            muts = gb.mutate()
            self.assertLessEqual(muts, 10)
            self.assertGreaterEqual(muts, 0)

    def test_crossover(self):   
        g1 = GenomeBase()
        g2 = GenomeBase()
        g3g4 = g1.crossover(g2)
        
        # check the correct type of object was returned
        self.assertEqual(len(g3g4), 2)
        self.assertIs(type(g3g4[0]), GenomeBase)
        self.assertIs(type(g3g4[1]), GenomeBase)
        
        # Check they are new objects
        self.assertNotEqual(g1, g3g4[0])
        self.assertNotEqual(g2, g3g4[0])
        self.assertNotEqual(g1, g3g4[1])
        self.assertNotEqual(g2, g3g4[1])

    def test_copy(self):
        gb = GenomeBase()
        gb2 = gb.copy()
        gl = gb.genome_list()
        gl2 = gb2.genome_list()
        self.assertEqual(gl, gl2)
        
        # change the gl2 and make sure gl doesn't change
        gl2[random.choice(gl2.keys())] = 11
        self.assertNotEqual(gl,gl2)

class TestGraphManager(unittest.TestCase):

    def test_add_variable(self):
        gm = GraphManager()
        v = gm.add_variable("a", "b+c")
        self.assertEqual(v.get_name(), "a")
        self.assertIn("b", v._depends_on)
        self.assertIn("c", v._depends_on)
        self.assertIn(v, gm._vars)

    def test_add_variable_twice_raises_attribute_error(self):
        gm = GraphManager()
        v = gm.add_variable("a", "b+c")
        with self.assertRaises(ConfigurationException):
            gm.add_variable("a", "d+e")

    def test_loads_json(self):
        gm = GraphManager()
        js_str = ""
        with open("test_data/basic.json", "r") as f:
            js_str = f.read()
        gm.load_json(js_str)
        
        # check all the variables were loaded properly
        vars = sorted([x.get_name() for x in gm._vars])
        expected = ['a','b','c','d','e']
        self.assertEquals(vars,expected)
        
        # check no relationship has been built for a and b
        vars = [x for x in gm._vars if x.get_name() == "a" or x.get_name() == "b"]
        self.assertEqual(len(vars), 2)
        self.assertEqual(vars[0]._expression, None)
        self.assertEqual(vars[1]._expression, None)
        
        # check a relationship was built for d
        vars = [x for x in gm._vars if x.get_name() == "d"]
        self.assertEquals(len(vars), 1)
        self.assertEquals(vars[0]._relationship, "c + a + b")
        
        # check initial conditions were loaded properly
        self.assertEquals(len(gm._inputs), 2)
        self.assertEquals(gm._inputs["a"], sp.S("1"))

    def test_unspecified_vars(self):
        gm = GraphManager()
        js_str = ""
        with open("test_data/basic_incomplete.json", "r") as f:
            js_str = f.read()
        gm.load_json(js_str)
        
        self.assertEquals(gm.get_missing_vars(), ['e'])

    def test_solver_complete(self):
        gm = GraphManager()
        js_str = ""
        with open("test_data/basic.json", "r") as f:
            js_str = f.read()
        gm.load_json(js_str)
        gm.resolve({}, False)

    def test_solver_incomplete(self):
        gm = GraphManager()
        js_str = ""
        with open("test_data/basic_incomplete.json", "r") as f:
            js_str = f.read()
        gm.load_json(js_str)
        
        with self.assertRaises(SolverException):
            gm.resolve({}, False)

class TestGraphVariable(unittest.TestCase):
    """Run some basic unit tests on the GraphVariable class"""
    
    def test_load_without_expression(self):
        v = GraphVariable("test")
        self.assertEqual(v._expression, None)
        self.assertEqual(v.get_name(), "test")

    def test_load_with_expression(self):
        v = GraphVariable("a", "b+c")
        self.assertIs(type(v._expression), sp.Add)
        self.assertEqual(v.get_name(), "a")
        
    def test_get_name(self):
        v = GraphVariable("test_name")
        self.assertEqual(v.get_name(), "test_name")

    def test_derive_dependents(self):
        v = GraphVariable("test_derive","a+b+c")
        self.assertEqual(['a','b','c'], sorted(v._depends_on))

    def test_dependency_list(self):
        v = GraphVariable("d","a+b+c")
        self.assertEqual([['a', 'd'],['b', 'd'],['c', 'd']], v.get_dependency_list())

    def test_solve_valid(self):
        v = GraphVariable("a", "b+c")
        inputs = {"b":1,"c":2}
        result = v.solve(inputs)
        self.assertEqual(result['a'], 3)

    def test_solve_with_missing_inputs_raises_attribute_error(self):
        v = GraphVariable("a", "b+c")
        inputs = {"b":1}
        with self.assertRaises(SolverException):
            v.solve(inputs)
    
    def test_solve_retains_unrequired_inputs(self):
        v = GraphVariable("a", "b+c")
        inputs = {"b":1,"c":2,"z":5}
        result = v.solve(inputs)
        self.assertIn("a", result)
        self.assertIn("b", result)
        self.assertIn("c", result)
        self.assertIn("z", result)
        self.assertEqual(result['a'], 3)

    def test_relationship_references_self_throws_attribute_error(self):
        with self.assertRaises(ConfigurationException):
            v = GraphVariable("a","a+b")


if __name__ == '__main__':
    unittest.main()