from conan import ConanFile
from conan.internal import check_duplicated_generator
from conan.tools.files import save
from os.path import join
# from posixpath import normpath

FASTBUILD_FILE = "conandeps.bff"

class _FastBuildTemplate(object):
    def __init__(self, deps_cpp_info):
        self.includedirs = ', '.join([f'"{p}"' for p in [v.replace('\\', '/') for v in deps_cpp_info.includedirs]])
        self.libdirs = ', '.join([f'"{p}"' for p in [v.replace('\\', '/') for v in deps_cpp_info.libdirs]])
        self.bindirs = ', '.join([f'"{p}"' for p in [v.replace('\\', '/') for v in deps_cpp_info.bindirs]])

        libs_list = [f'"{p}"' for p in [v.replace('"', '\\"') for v in deps_cpp_info.libs]]
        libs_list.extend([f'"{p}"' for p in [v.replace('"', '\\"') for v in deps_cpp_info.system_libs]])
        libs_list.extend([f'"{p}"' for p in [v.replace('"', '\\"') for v in deps_cpp_info.frameworks]])
        self.libs = ', '.join(libs_list)
        self.defines = ', '.join([f'"{p}"' for p in [v.replace('"', '\\"') for v in deps_cpp_info.defines]])

class FastBuildDeps(object):
    def __init__(self, conanfile):
        self._conanfile = conanfile

    def generate(self, output_path=None):
        check_duplicated_generator(self, self._conanfile)
        # Current directory is the generators_folder
        generator_files = self.content
        for generator_file, content in generator_files.items():
            if output_path != None:
                generator_file = join(output_path, generator_file)
            save(self, generator_file, content)

    def _get_cpp_info(self):
        ret = CppInfo()
        for dep in self._conanfile.dependencies.host.values():
            dep_cppinfo = dep.cpp_info.copy()
            dep_cppinfo.set_relative_base_folder(dep.package_folder)
            # In case we have components, aggregate them, we do not support isolated "targets"
            # dep_cppinfo.aggregate_components()
            ret.merge(dep_cppinfo)
        return ret

    @property
    def content(self):
        ret = {}  # filename -> file content

        host_req = self._conanfile.dependencies.host
        test_req = self._conanfile.dependencies.test

        dependency_template = (
            '// "name": "{package_name}", "package_folder": "{folder}"\n'
            '.ConanModuleEntry =\n'
            '[\n'
            '    .ConanModule_{name} =\n'
            '    [\n'
            '        .IncludeDirs = {{{deps.includedirs}}}\n'
            '        .Defines = {{{deps.defines}}}\n'
            '        .LibDirs = {{{deps.libdirs}}}\n'
            '        .Libs = {{{deps.libs}}}\n'
            '        .BinDirs = {{{deps.bindirs}}}\n'
            '    ]\n'
            ']\n'
            '.ConanModules + .ConanModuleEntry\n')

        sections = ['.ConanModules = [ ]']

        # Iterate all the transitive requires
        for require, dep in list(host_req.items()) + list(test_req.items()):
            deps = _FastBuildTemplate(dep.cpp_info)
            dep_name = dep.ref.name.replace("-", "_")
            dep_flags = dependency_template.format(package_name=dep.ref.name, folder=dep.package_folder, name=dep_name, deps=deps)
            sections.append(dep_flags)

        ret[FASTBUILD_FILE] = "\n".join(sections)
        return ret


# The package description
class FASTBuildGeneratorPackage(ConanFile):
    name = "fastbuild-generator"
    version = "0.4.2"
    user = "iceshard"
    channel = "stable"

    license = "MIT"
    url = "https://github.com/iceshard-engine/conan-recipes/"
    description = "FASTBuild generator for the conan package manager."
