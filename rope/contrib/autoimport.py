from rope.refactor import importutils

class AutoImport(object):

    def __init__(self, project):
        self.project = project
        self.names = project.data_files.read_data('globalnames')
        if self.names is None:
            self.names = {}
        project.data_files.add_write_hook(self.write)

    def write(self):
        self.project.data_files.write_data('globalnames', self.names)

    def get_imports(self, starting):
        # XXX: breaking if gave up! use generators
        result = []
        for module in self.names:
            for global_name in self.names[module]:
                if global_name.startswith(starting):
                    result.append((global_name, module))
        return result

    def update_resource(self, resource):
        # XXX: what if there are syntax errors
        pymodule = self.project.pycore.resource_to_pyobject(resource)
        modname = importutils.get_module_name(self.project.pycore,
                                              resource)
        self._add_names(pymodule, modname)

    def _add_names(self, pymodule, modname):
        # XXX: exclude imported names
        globals = [x for x in pymodule._get_structural_attributes()]
        self.names[modname] = globals

    def update_module(self, modname):
        # XXX: what if module cannot be found?
        pymodule = self.project.pycore.get_module(modname)
        self._add_names(pymodule, modname)
