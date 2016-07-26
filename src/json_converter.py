try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import yaml
import logging
import json
from docopt import docopt


##########################################################################
############################ HELPER FUNCTIONS ############################
##########################################################################


def dynamic_import(modulename, classname):
    mod = __import__(modulename)
    components = modulename.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return getattr(mod, classname)

##########################################################################
############################## HELPER CLASS ##############################
##########################################################################


class mapping_function_param(object):
    def __init__(self, param_dict):
        self._functions = []
        self._name = None
        self._value = None
        for k in param_dict.keys():
            if k == 'functions':
                for f in param_dict.get(k):
                    self._functions.append(mapping_function(f))
            else:
                self._name = k
                self._value = param_dict[self._name]
        

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def functions(self):
        return self._functions
    
    

class mapping_function(object):
    def __init__(self, func_dict):
        self._module = func_dict.get('module')
        self._function = func_dict.get('function')
        self._params = []

        if func_dict.get('params'):
            for param in func_dict.get('params'):
                self._params.append(mapping_function_param(param))

    @property
    def module(self):
        return self._module

    @property
    def function(self):
        return self._function

    @property
    def params(self):
        return self._params
        

class mapping_node(object):
    def __init__(self, node_data):
        self._source    = node_data.get('source')
        self._dest      = node_data.get('destination')
        self._default   = node_data.get('default_value',None)
        self._functions = []
        self._is_list   = node_data.get('list',False)

        if node_data.get('functions'):
            for f in node_data.get('functions'):
                self._functions.append(mapping_function(f))

    def __tolist(self, x):
        if '.' in x:
            return x.split('.')
        return [x]

    @property
    def source(self):
        return self._source

    @property
    def sourcel(self):
        return self.__tolist(self.source)

    @property
    def destination(self):
        return self._dest

    @property
    def destinationl(self):
        return self.__tolist(self.destination)
    

    @property
    def default(self):
        return self._default

    @property
    def functions(self):
        return self._functions

    @property
    def is_list(self):
        return self._is_list
    


    def __str__(self):
        msg =  '''
            source  : {0}
            dest    : {1}
            default : {2}
        '''.format(self.source, self.destination, self.default)    

        for f in self.functions:
            msg += '''
                functions:
                    module   : {0}
                    function : {1}
            '''.format(f.module,f.function)

            for p in f.params:
                if p.name is not None and p.value is not None:
                    msg += '''
                    params:
                        {0} : {1}
                    '''.format(p.name,p.value)

                for f in p.functions:
                    msg += '''
                        functions:
                            module   : {0}
                            function : {1}
                    '''.format(f.module,f.function)

        return msg

##########################################################################
######################## BUILTIN CONVERSION CLASS ########################
##########################################################################

class builtin_conversion(object):
    def to_node(self, value, params=[]):
        d = {}
        for p in params:
            if p.name == 'node':
                if type(value) == list:
                    pass
                if type(value) == dict:
                    for k in value.keys():
                        d.update({k:{p.value:value.get(k)}})
                else:
                    d.update({p.value:value})        
        return d

    def to_bool_node(self, value, params=[]):
        res = {}
        if type(value) == list:
            for v in value:
                res.update({v:True})
        else:
            res.update({value:True})

        return res

    def add_tag(self, value, params):
        for p in params:
            if type(value) == dict:
                value.update({p.name:p.value})

        return value

    def map(self, value, params=None):
        res = []
        if value:
            for p in params:
                for f in p.functions:
                    module = f.module.split('.')
                    func_class = dynamic_import(module[0],module[1])
                    func_class_instance = func_class()
                    func = getattr(func_class_instance,f.function)
                    for v in value:
                        res_val = func(v,f.params)
                        res.append(res_val)
        return res
        

    def __base_check(self, value):
        if value is None:
            return None
        if type(value) == str or type(value) == unicode:
            if value == '':
                return None
        return value

    def to_int(self, value, params=None):
        if self.__base_check(value) is None:
            return None
        return int(value)

    def to_bool(self, value, params=None):
        if self.__base_check(value) is None:
            return False
        if type(value) == unicode:
            if value.lower() == u'true':
                return True
            elif value.lower() == u'false':
                return False
        return bool(value)


    def to_float(self, value, params=None):
        if self.__base_check(value) is None:
            return None
        return float(value)

    def to_string(self, value, params=None):
        if self.__base_check(value) is None:
            return None
        return str(value)

    def to_datetime(self, value, params=None):
        if not value:
            return None
        if value == 0 or value is None:
            return None
        import datetime
        return datetime.datetime.fromtimestamp(float(value)).strftime('%Y-%m-%d %H:%M:%S')


    def remove_key(self, value, params=None):
        if type(value) == dict:
            for k in value.keys():
                return value.get(k)

        return []

    def load_json(self, value, params=None):
        if self.__base_check(value) is None:
            return None
        try:
            json_value = json.loads(value)
            return json_value
        except:
            return None

    def to_dict(self, value, params):
        if self.__base_check(value) is None:
            return None

        sep = None
        for p in params:
            if p.name == 'separator':
                sep = p.value

        if sep:
            res = {}
            for v in value.split('.'):
                res.update(v)
            return res

        return value

    def to_list(self, value, params):
        if self.__base_check(value) is None:
            return None

        sep = None
        for p in params:
            if p.name == 'separator':
                sep = p.value

        if sep:
            return value.split(sep)

        return value

    def replace(self, value, params):
        s_param = None
        d_param = None

        for p in params:
            if p.name == 'source':
                s_param = p.value
            if p.name == 'destination':
                d_param = p.value

        if s_param and d_param:
            if type(value) in [unicode, str]:
                return value.replace(s_param, d_param)

        if s_param:
            if type(value) in [unicode, str]:
                return value.replace(s_param, "").strip()

        return value

    def clean_field(self, value, params):
        res = ''
        if type(value) in [str, unicode]:
            for c in value:
                if c != '\"':
                    res += c
        return res

##########################################################################
######################## DEFAULT CONVERSION CLASS ########################
##########################################################################

class default_conversion(object):
    def to_upper(self, string_value,params=None):
        return string_value.upper()

    def to_lower(self, string_value,params=None):
        return string_value.lower()

    def strip(self, string_value,params=None):
        return string_value.strip()

class media_conversion(object):
    def to_media(self, value, params=None):
        for v in value:
            for p in params:
                v.update({p.name:p.value})

        return value

######################################################################################
#################################### JSON Walker #####################################
######################################################################################


class JsonWalker(object):
    @staticmethod
    def walkto(node, paths):
        if node is None:
            return None
        elif len(paths) == 1:
            return node.get(paths[0],None)
        else:
            return JsonWalker.walkto(node.get(paths[0]),paths[1:])

    @staticmethod
    def addto(node,paths,value,create_not_found=False,is_list=False):
        if node is None:
            return False
        if len(paths) == 1:
            tmp_n = node.get(paths[0])
            if  tmp_n is None and not is_list:
                node.update({paths[0]:value})
            elif tmp_n is None and is_list:
                node.update({paths[0]:[value]})
            else:
                if type(tmp_n) == list and type(value) == list:
                    for v in value:
                        tmp_n.append(v)
                elif type(tmp_n) == list:
                    tmp_n.append(value)
            return True
        else:
            if not node.get(paths[0]):
                if create_not_found:
                    node.update({paths[0]:{}})
                else:
                    return False
            return JsonWalker.addto(node.get(paths[0]),paths[1:],value,create_not_found,is_list)

    @staticmethod
    def remove(node,paths):
        if node is None:
            return False
        if len(paths) == 1:
            node.pop(paths[0])
        else:
            if not node.get(paths[0]):
                return False
            return JsonWalker.remove(node.get(paths[0]),paths[1:])

##########################################################################
############################# JSON CONVERTER #############################
##########################################################################
SPECIAL_FUNCTIONS = ['map']

class document_converter(object):
    def __init__(self, mapping_file, logger=None):
        if logger is None:
            self._logger = logging.getLogger('JsonConverter')
        else:
            self._logger = logger

        f = open(mapping_file,'r')
        self._mappings = yaml.load(f)

    @property
    def mappings(self):
        return self._mappings.get('mappings')

    @property
    def nodes(self):
        res = []
        for node in self.mappings:
            n = mapping_node(node)
            res.append(n)

        return res

    def apply_function(self, value, module_name, function_name, params=[]):
        module = module_name.split('.')
        func_class = dynamic_import(module[0],module[1])
        func_class_instance = func_class()
        func = getattr(func_class_instance,function_name)
        res_val = func(value,params)
        self._logger.debug(' Val %s'%(res_val))
        # Apply nested functions if present
        if function_name not in SPECIAL_FUNCTIONS:
            for p in params:
                for f in p.functions:
                    self._logger.debug(' Apply nested function %s.%s'%(f.module,f.function))
                    res_val = self.apply_function(res_val,f.module, f.function, f.params)
                    self._logger.debug(' Val %s'%(res_val))

        return res_val

    def convert(self, source_doc, destination_doc, mapping_empty_fields=True):
        for node in self.nodes:
            self._logger.debug(' source : %s'%(node.sourcel))
            source_val = JsonWalker.walkto(source_doc, node.sourcel)
            self._logger.debug(' source val : %s'%(source_val))

            destination_val = source_val

            # Apply functions
            for f in node.functions:
                self._logger.debug(' Appy function : %s.%s',f.module,f.function)
                for p in f.params:
                    self._logger.debug('        params : %s,%s',p.name,p.value)
                destination_val = self.apply_function(destination_val, f.module, f.function, f.params)
                if destination_val is None:
                    destination_val = node.default

            if (destination_val is not None and destination_val != "") or mapping_empty_fields:
                if not JsonWalker.addto(destination_doc,node.destinationl, destination_val,create_not_found=True,is_list=node.is_list):
                    self._logger.error(" Unable to map data : %s | %s"%(node.destination, destination_val))
                    return False

        return True

##########################################################################
############################### MAIN TEST ################################
##########################################################################

options = """
JsonConverter.

Usage:
    json_converter.py -m MAPPING -j JSON [-l LOGLEVEL]

Options:
    -m MAPPING                      yaml mapping file
    -j JSON                         json source file
    -h --help                       show this screen
    -l LOGLEVEL --loglevel=LOGLEVEL log level [default:INFO]
    --version                       show version information

"""

if __name__ == '__main__':
    args = docopt(options, version='JsonConverter 0.1')

    log_level = logging.INFO
    if args.get('--loglevel'):
        if args.get('--loglevel') == 'DEBUG':
            log_level = logging.DEBUG
        elif args.get('--loglevel') == 'WARNING':
            log_level = logging.WARNING

    logging.basicConfig()
    logger = logging.getLogger('JsonConverter')
    logger.setLevel(log_level)

    f = open(args.get('-j'),'r')
    source_file = json.load(f)
    jc = document_converter(args.get('-m'),logger)

    dest_json = {}
    if jc.convert(source_file, dest_json):
        logger.info(json.dumps(dest_json,indent=4,ensure_ascii=False))


