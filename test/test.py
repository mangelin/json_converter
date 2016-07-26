import unittest
import json
import json_converter

f = open('data/test_1.json','r')
source_data = json.load(f)
jc = json_converter.document_converter('etc/mapping_test.yml')

class json_converter_test(unittest.TestCase):
    
    def test_conversion(self):
        result_data = {}
        result = jc.convert(source_data,result_data)    
        self.assertEqual(result,True)

    def test_int_field(self):
        result_data = {}
        result = jc.convert(source_data,result_data)    
        self.assertEqual(json_converter.JsonWalker.walkto(result_data,['field','int','value']),12345) 

    def test_bool_field(self):       
        result_data = {}
        result = jc.convert(source_data,result_data)    
        self.assertEqual(json_converter.JsonWalker.walkto(result_data,['field','bool','value']),False) 

    def test_string_field(self):       
        result_data = {}
        result = jc.convert(source_data,result_data)    
        self.assertEqual(json_converter.JsonWalker.walkto(result_data,['field','string','value']),"TESTNAME") 

    def test_listField_field(self):
        result_data = {}
        result = jc.convert(source_data,result_data)    
        self.assertEqual(json_converter.JsonWalker.walkto(result_data,['field','list_field']),[{'type':'image','file':'1.jpg'},{'type':'image','file':'2.jpg'}])

    def test_toListField_field(self):
        result_data = {}
        result = jc.convert(source_data,result_data)    
        self.assertEqual(json_converter.JsonWalker.walkto(result_data,['field','list','elements']),[{'match' : {'value':'value1'}},{'match' : {'value':'value2'}}])

if __name__ == '__main__':
    result_data = {}
    result = jc.convert(source_data,result_data)    
    print '*** ORIGINAL JSON ***'
    print json.dumps(source_data, indent=4)
    print '*** MAPPED JSON ***'
    print json.dumps(result_data, indent=4)

    print '*** TEST ***'
    suite_1 = unittest.TestLoader().loadTestsFromTestCase(json_converter_test)
    unittest.TextTestRunner(verbosity=2).run(suite_1)