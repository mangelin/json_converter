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
        print json.dumps(result_data, indent=4)   
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


if __name__ == '__main__':
    suite_1 = unittest.TestLoader().loadTestsFromTestCase(json_converter_test)
    unittest.TextTestRunner(verbosity=2).run(suite_1)