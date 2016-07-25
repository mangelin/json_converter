import unittest
import json
import json_converter

f = open('data/test.json','r')
source_data = json.load(f)
jc = json_converter.document_converter('etc/mapping_listing_test.yml')

class json_converter_test(unittest.TestCase):
    
    def test_conversion(self):
        result_data = {}
        result = jc.convert(source_data,result_data)    
        self.assertEqual(result,True)

    def test_id(self):
        result_data = {}
        result = jc.convert(source_data,result_data)    
        self.assertEqual(json_converter.JsonWalker.walkto(result_data,['property','id']),29434862) 

    def test_bool_data(self):       
        result_data = {}
        result = jc.convert(source_data,result_data)    
        self.assertEqual(json_converter.JsonWalker.walkto(result_data,['property','features','efficency','is_quite_zero_energy_state','value']),False) 


if __name__ == '__main__':
    suite_1 = unittest.TestLoader().loadTestsFromTestCase(json_converter_test)
    unittest.TextTestRunner(verbosity=2).run(suite_1)