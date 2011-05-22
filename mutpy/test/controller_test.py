import unittest
import os
import shutil
import types
import tempfile
import sys

from mutpy import controller


class ModulesLoaderTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='mutpytmp-') + '/'
        sys.path.append(cls.tmp)
        os.makedirs(cls.tmp + 'a/b/c')
        open(cls.tmp + 'a/__init__.py', 'w').close()
        open(cls.tmp + 'a/b/__init__.py', 'w').close()
        open(cls.tmp + 'a/b/c/__init__.py', 'w').close()
        with open(cls.tmp + 'a/b/c/sample.py', 'w') as f:
            f.write('class X:\n\tdef f():\n\t\tpass')
            
    
    def setUp(self):
        self.loader = controller.ModulesLoader(None, None)
        
    def test_load_file(self):
        module, to_mutate = self.loader.load(ModulesLoaderTest.tmp + 'a/b/c/sample.py')
        
        self.assertIsNone(to_mutate)
        self.assertIsInstance(module, types.ModuleType)
        self.assertTrue(hasattr(module, 'X'))
        self.assertMultiLineEqual(module.__file__, ModulesLoaderTest.tmp + 'a/b/c/sample.py')
        self.assertMultiLineEqual(module.__name__, 'sample')
        
    def test_load_module(self):
        module, to_mutate = self.loader.load('a.b.c.sample')
        
        self.assertIsNone(to_mutate)
        self.assertIsInstance(module, types.ModuleType)
        self.assertTrue(hasattr(module, 'X'))
        self.assertMultiLineEqual(module.__file__, ModulesLoaderTest.tmp + 'a/b/c/sample.py')
        self.assertMultiLineEqual(module.__name__, 'a.b.c.sample')
        
    def test_target_class(self):
        module, to_mutate = self.loader.load('a.b.c.sample.X')
        
        self.assertMultiLineEqual(to_mutate, 'X')
        self.assertIsInstance(module, types.ModuleType)
        self.assertTrue(hasattr(module, 'X'))
        self.assertMultiLineEqual(module.__file__, ModulesLoaderTest.tmp + 'a/b/c/sample.py')
        self.assertMultiLineEqual(module.__name__, 'a.b.c.sample')
    
    def test_target_method(self):
        module, to_mutate = self.loader.load('a.b.c.sample.X.f')
        
        self.assertMultiLineEqual(to_mutate, 'X.f')
        self.assertIsInstance(module, types.ModuleType)
        self.assertTrue(hasattr(module, 'X'))
        self.assertMultiLineEqual(module.__file__, ModulesLoaderTest.tmp + 'a/b/c/sample.py')
        self.assertMultiLineEqual(module.__name__, 'a.b.c.sample')
        
    def test_bad_target_class(self):
        self.assertRaises(controller.ModulesLoaderException, lambda : self.loader.load('a.b.c.sample.Y'))
    
    def test_bad_target_method(self):
        self.assertRaises(controller.ModulesLoaderException, lambda : self.loader.load('a.b.c.sample.X.g'))
        
    def test_bad_module(self):    
        self.assertRaises(controller.ModulesLoaderException, lambda : self.loader.load('a.b.c.example'))
    
    def test_bad_file(self):    
        self.assertRaises(controller.ModulesLoaderException, lambda : self.loader.load('a/b/c/example.py'))
        
        
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)
        
        
class MutationScoreTest(unittest.TestCase):
    
    def test_score(self):
        score = controller.MutationScore(all_mutants=11, killed_mutants=5, incompetent_mutants=1)
        self.assertEqual(score.count(), 50)
        score.inc_killed()
        self.assertEqual(score.count(), 60)
        
    def test_zero_score(self):
        score = controller.MutationScore(all_mutants=0)
        self.assertEqual(score.count(), 0)