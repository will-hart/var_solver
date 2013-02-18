import unittest
import sympy as sp

from GraphManager import GraphManager
from GraphVariable import GraphVariable


class TestGraphManager(unittest.TestCase):
    def test_finish_tests(self):
        self.assertTrue(False)

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
        with self.assertRaises(AttributeError):
            gm.add_variable("a", "d+e")


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
        with self.assertRaises(AttributeError):
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


if __name__ == '__main__':
    unittest.main()