import os
import sys
import pprint

def get_all_depends(modules, addons_paths, depends=None):
    if depends is None:
        depends = []
    for module in (modules or '').split(','):
        if not module in depends:
            depends.append( module )
            for addons_path in (addons_paths or '').split(','):
                addons_path = addons_path.strip()
                fname_openerp = os.path.join( addons_path, module, '__openerp__.py' )
                if os.path.isfile( fname_openerp ):
                    module_depends_list = eval( open(fname_openerp, "r").read() ).get('depends', [])
                    if module_depends_list:
                        module_depends_str = ','.join( module_depends_list )
                        get_depends(module_depends_str, addons_paths, depends=depends)
    return depends

def get_modules_depends_dict(addons_paths):
    if isinstance(addons_paths, str) or isinstance(addons_paths, basestring):
        addons_paths = addons_paths.split(',')
    modules_depends_dict = {}
    for addons_path in addons_paths:
        for addon_path in os.listdir(addons_path):
            oerp_path = os.path.join(addon_path, "__openerp__.py")
            if os.path.isfile(oerp_path):
                module_depends_list = eval( open(oerp_path, "r").read() ).get('depends', [])
                modules_depends_dict[os.path.dirname(oerp_path)] = module_depends_list
    return modules_depends_dict

def print_modules_depends_dict(modules_depends_dict):
    for key in sorted(modules_depends_dict.keys()):
        print key + ':',
        print '\n\t' + '\n\t'.join(modules_depends_dict[key])
            
if __name__ == '__main__':
    modules_depends_dict = get_modules_depends_dict(sys.argv[1])
    print_modules_depends_dict(modules_depends_dict)
    #for key in sorted(modules_depends_dict.keys()):
        #print "key",key,
        #print "modules", '\n\t'.join(modules_depends_dict[key])
    #pp = pprint.PrettyPrinter(indent=4)
    #print pp.pprint(modules_depends_dict)
