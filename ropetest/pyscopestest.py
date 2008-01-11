import unittest

from rope.base.pyobjects import get_base_type
from ropetest import testutils


class PyCoreScopesTest(unittest.TestCase):

    def setUp(self):
        super(PyCoreScopesTest, self).setUp()
        self.project = testutils.sample_project()
        self.pycore = self.project.get_pycore()

    def tearDown(self):
        testutils.remove_project(self.project)
        super(PyCoreScopesTest, self).tearDown()

    def test_simple_scope(self):
        scope = self.pycore.get_string_scope('def sample_func():\n    pass\n')
        sample_func = scope['sample_func'].get_object()
        self.assertEquals(get_base_type('Function'), sample_func.get_type())

    def test_simple_function_scope(self):
        scope = self.pycore.get_string_scope(
            'def sample_func():\n    a = 10\n')
        self.assertEquals(1, len(scope.get_scopes()))
        sample_func_scope = scope.get_scopes()[0]
        self.assertEquals(1, len(sample_func_scope.get_names()))
        self.assertEquals(0, len(sample_func_scope.get_scopes()))

    def test_classes_inside_function_scopes(self):
        scope = self.pycore.get_string_scope(
            'def sample_func():\n'
            '    class SampleClass(object):\n        pass\n')
        self.assertEquals(1, len(scope.get_scopes()))
        sample_func_scope = scope.get_scopes()[0]
        self.assertEquals(get_base_type('Type'),
                          scope.get_scopes()[0]['SampleClass'].get_object().get_type())

    def test_simple_class_scope(self):
        scope = self.pycore.get_string_scope(
            'class SampleClass(object):\n'
            '    def f(self):\n        var = 10\n')
        self.assertEquals(1, len(scope.get_scopes()))
        sample_class_scope = scope.get_scopes()[0]
        self.assertEquals(1, len(sample_class_scope.get_names()))
        self.assertEquals(1, len(sample_class_scope.get_scopes()))
        f_in_class = sample_class_scope.get_scopes()[0]
        self.assertTrue('var' in f_in_class.get_names())

    def test_get_lineno(self):
        scope = self.pycore.get_string_scope(
            '\ndef sample_func():\n    a = 10\n')
        self.assertEquals(1, len(scope.get_scopes()))
        sample_func_scope = scope.get_scopes()[0]
        self.assertEquals(1, scope.get_start())
        self.assertEquals(2, sample_func_scope.get_start())

    def test_scope_kind(self):
        scope = self.pycore.get_string_scope(
            'class SampleClass(object):\n    pass\n'
            'def sample_func():\n    pass\n')
        sample_class_scope = scope.get_scopes()[0]
        sample_func_scope = scope.get_scopes()[1]
        self.assertEquals('Module', scope.get_kind())
        self.assertEquals('Class', sample_class_scope.get_kind())
        self.assertEquals('Function', sample_func_scope.get_kind())

    def test_function_parameters_in_scope_names(self):
        scope = self.pycore.get_string_scope(
            'def sample_func(param):\n    a = 10\n')
        sample_func_scope = scope.get_scopes()[0]
        self.assertTrue('param' in sample_func_scope.get_names())

    def test_get_names_contains_only_names_defined_in_a_scope(self):
        scope = self.pycore.get_string_scope(
            'var1 = 10\ndef sample_func(param):\n    var2 = 20\n')
        sample_func_scope = scope.get_scopes()[0]
        self.assertTrue('var1' not in sample_func_scope.get_names())

    def test_scope_lookup(self):
        scope = self.pycore.get_string_scope(
            'var1 = 10\ndef sample_func(param):\n    var2 = 20\n')
        self.assertTrue(scope.lookup('var2') is None)
        self.assertEquals(get_base_type('Function'),
                          scope.lookup('sample_func').get_object().get_type())
        sample_func_scope = scope.get_scopes()[0]
        self.assertTrue(sample_func_scope.lookup('var1') is not None)

    def test_function_scopes(self):
        scope = self.pycore.get_string_scope('def func():\n    var = 10\n')
        func_scope = scope.get_scopes()[0]
        self.assertTrue('var' in func_scope.get_names())

    def test_function_scopes_classes(self):
        scope = self.pycore.get_string_scope(
            'def func():\n    class Sample(object):\n        pass\n')
        func_scope = scope.get_scopes()[0]
        self.assertTrue('Sample' in func_scope.get_names())

    def test_function_getting_scope(self):
        mod = self.pycore.get_string_module('def func():    var = 10\n')
        func_scope = mod['func'].get_object().get_scope()
        self.assertTrue('var' in func_scope.get_names())

    def test_scopes_in_function_scopes(self):
        scope = self.pycore.get_string_scope(
            'def func():\n    def inner():\n        var = 10\n')
        func_scope = scope.get_scopes()[0]
        inner_scope = func_scope.get_scopes()[0]
        self.assertTrue('var' in inner_scope.get_names())

    def test_for_variables_in_scopes(self):
        scope = self.pycore.get_string_scope(
            'for a_var in range(10):\n    pass\n')
        self.assertTrue('a_var' in scope.get_names())

    def test_assists_inside_fors(self):
        scope = self.pycore.get_string_scope(
            'for i in range(10):\n    a_var = i\n')
        self.assertTrue('a_var' in scope.get_names())

    def test_first_parameter_of_a_method(self):
        code = 'class AClass(object):\n' \
               '    def a_func(self, param):\n        pass\n'
        a_class = self.pycore.get_string_module(code)['AClass']. get_object()
        function_scope = a_class['a_func'].get_object().get_scope()
        self.assertEquals(a_class, function_scope['self'].get_object().get_type())
        self.assertNotEquals(a_class, function_scope['param'].
                             get_object().get_type())

    def test_first_parameter_of_static_methods(self):
        code = 'class AClass(object):\n' \
               '    @staticmethod\n    def a_func(param):\n        pass\n'
        a_class = self.pycore.get_string_module(code)['AClass']. get_object()
        function_scope = a_class['a_func'].\
                         get_object().get_scope()
        self.assertNotEquals(a_class, function_scope['param'].get_object().get_type())

    def test_first_parameter_of_class_methods(self):
        code = 'class AClass(object):\n' \
            '    @classmethod\n    def a_func(cls):\n        pass\n'
        a_class = self.pycore.get_string_module(code)['AClass']. get_object()
        function_scope = a_class['a_func'].get_object().get_scope()
        self.assertEquals(a_class, function_scope['cls'].get_object())

    def test_first_parameter_with_self_as_name_and_unknown_decorator(self):
        code = 'def my_decorator(func):\n    return func\n'\
               'class AClass(object):\n' \
               '    @my_decorator\n    def a_func(self):\n        pass\n'
        a_class = self.pycore.get_string_module(code)['AClass']. get_object()
        function_scope = a_class['a_func'].get_object().get_scope()
        self.assertEquals(a_class, function_scope['self'].
                          get_object().get_type())

    def test_inside_class_scope_attribute_lookup(self):
        scope = self.pycore.get_string_scope(
            'class C(object):\n'
            '    an_attr = 1\n'
            '    def a_func(self):\n        pass')
        self.assertEquals(1, len(scope.get_scopes()))
        c_scope = scope.get_scopes()[0]
        self.assertEquals(2, len(c_scope.get_names()))
        self.assertTrue(c_scope.lookup('an_attr') is not None)
        f_in_c = c_scope.get_scopes()[0]
        self.assertTrue(f_in_c.lookup('an_attr') is None)

    def test_inside_class_scope_attribute_lookup2(self):
        scope = self.pycore.get_string_scope(
            'class C(object):\n'
            '    def __init__(self):\n        self.an_attr = 1\n'
            '    def a_func(self):\n        pass')
        self.assertEquals(1, len(scope.get_scopes()))
        c_scope = scope.get_scopes()[0]
        f_in_c = c_scope.get_scopes()[0]
        self.assertTrue(f_in_c.lookup('an_attr') is None)

    def test_get_inner_scope_for_staticmethods(self):
        scope = self.pycore.get_string_scope(
            'class C(object):\n'
            '    @staticmethod\n'
            '    def a_func(self):\n        pass\n')
        c_scope = scope.get_scopes()[0]
        f_in_c = c_scope.get_scopes()[0]
        self.assertEquals(f_in_c, scope.get_inner_scope_for_line(4))

    def test_getting_overwritten_scopes(self):
        scope = self.pycore.get_string_scope(
            'def f():\n    pass\ndef f():\n    pass\n')
        self.assertEquals(2, len(scope.get_scopes()))
        f1_scope = scope.get_scopes()[0]
        f2_scope = scope.get_scopes()[1]
        self.assertNotEquals(f1_scope, f2_scope)

    def test_assigning_builtin_names(self):
        mod = self.pycore.get_string_module('range = 1\n')
        range = mod.get_scope().lookup('range')
        self.assertEquals((mod, 1), range.get_definition_location())

    def test_get_inner_scope_and_logical_lines(self):
        scope = self.pycore.get_string_scope(
            'class C(object):\n'
            '    def f():\n        s = """\n1\n2\n"""\n        a = 1\n')
        c_scope = scope.get_scopes()[0]
        f_in_c = c_scope.get_scopes()[0]
        self.assertEquals(f_in_c, scope.get_inner_scope_for_line(7))


def suite():
    result = unittest.TestSuite()
    result.addTests(unittest.makeSuite(PyCoreScopesTest))
    return result


if __name__ == '__main__':
    unittest.main()
