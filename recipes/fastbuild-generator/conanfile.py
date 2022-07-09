from conans import ConanFile
from conans.model import Generator
from posixpath import normpath


conan_fastbuild_header = """
.ConanModules = [ ]
"""

conan_fastbuild_module = """
.ConanModuleEntry =
[
    .ConanModule_{name} =
    [
        .IncludeDirs = {{}}
        .Defines = {{}}
        .LibDirs = {{}}
        .Libs = {{}}
        .BinDirs = {{}}

    {properties}
    ]
]
.ConanModules + .ConanModuleEntry
"""

conan_fastbuild_header_with_config = """
.ConanModules_Debug = [ ]
.ConanModules_Release = [ ]
"""

conan_fastbuild_module_with_config = """
.ConanModuleEntry =
[
    .ConanModule_{name}_{config} =
    [
        .IncludeDirs = {{}}
        .Defines = {{}}
        .LibDirs = {{}}
        .Libs = {{}}
        .BinDirs = {{}}

    {properties}
    ]
]
.ConanModules_{config} + .ConanModuleEntry
"""


class FASTBuildDependencies(object):
    def __init__(self, source, base=None):
        # Get only unique attributes
        def get_unique(name):
            attrib = getattr(source, name, [])
            attrib_base = getattr(base, name, [])

            if base == None:
                return attrib

            if type(attrib) != list:
                return attrib

            return [item for item in attrib if item not in attrib_base]

        self.includedirs = get_unique('include_paths')
        self.libdirs = get_unique('lib_paths')
        self.bindirs = get_unique('bin_paths')
        self.links = get_unique('libs')
        self.defines = get_unique('defines')

        if base == None:
            if hasattr(source, 'debug'):
                self.debug = FASTBuildDependencies(source.debug, base=source)
            if hasattr(source, 'release'):
                self.release = FASTBuildDependencies(source.release, base=source)

    def has_cpp_info(self):
        return (self.includedirs
            or self.libdirs
            or self.defines
            or self.links
            or self.bindirs
        )


class FASTBuildModule(object):
    def __init__(self, name):
        self.name = name
        self.lines = []

    def append(self, str, indent = False):
        self.lines.append(str)

    def build_property(self, name, values, paths=False, IndentLevel=0):
        indent_prop = ''.join(["    "] * (IndentLevel + 1))
        indent_prop_arg = ''.join(["    "] * (IndentLevel + 2))
        lines = []

        if values:
            lines.append("%s%s + {" % (indent_prop, name))
            for value in values:
                if paths:
                    value = normpath(value).replace("\\", "/")
                lines.append('%s"%s",' % (indent_prop_arg, value))
            lines.append("%s}" % indent_prop)

        return lines

    def build_commands_property(self, dirs_from, to, command, files="*", stage="", IndentLevel=0):
        indent_prop = ''.join(["    "] * IndentLevel)
        indent_prop_arg = ''.join(["    "] * (IndentLevel + 1))
        lines = []

        if command not in ["copy"]:
            return lines

        # make sure we end the ratget dir with a slash
        to = normpath(to) + "/"

        if dirs_from:
            lines.append("%s%scommands{" % (indent_prop, stage))
            for dir_from in dirs_from:
                dir_from = normpath(dir_from).replace("\\", "/")
                # For the 'copy' command
                if command == "copy":
                    lines.append('%s\'{COPY} "%s/%s" "%s"\',' % (indent_prop_arg, dir_from, files, to))
            lines.append("%s}" % indent_prop)

        return lines


    def build_property_group(self, deps):

        indentation = 0

        lines = []
        lines += self.build_property(".Defines", deps.defines, False, IndentLevel=indentation)
        lines += self.build_property(".IncludeDirs", deps.includedirs, True, IndentLevel=indentation)
        lines += self.build_property(".LibDirs", deps.libdirs, True, IndentLevel=indentation)
        lines += self.build_property(".Libs", deps.links, False, IndentLevel=indentation)
        lines += self.build_property(".BinDirs", deps.bindirs, True, IndentLevel=indentation)

        return lines

    def build_conan_module(self, deps):

        properties = "\n    ".join(self.build_property_group(deps))
        # We want to replace all '-' occuratnes with '_' as fastbuild does not allow the former one to be used in variable names.
        self.append(conan_fastbuild_module.format(name=self.name.replace('-', '_'), properties=properties))
        return True

    def build(self, deps):
        if self.build_conan_module(deps):
            return '\n'.join(self.lines)
        return ''

class FASTBuildModuleMultiConfig(object):
    def __init__(self, name):
        self.name = name
        self.lines = []

    def append(self, str, indent = False):
        self.lines.append("%s" % str)

    def build_property(self, name, values, paths=False, IndentLevel=0):
        indent_prop = ''.join(["    "] * (IndentLevel + 1))
        indent_prop_arg = ''.join(["    "] * (IndentLevel + 2))
        lines = []

        if values:
            lines.append("%s%s + {" % (indent_prop, name))
            for value in values:
                if paths:
                    value = normpath(value).replace("\\", "/")
                lines.append('%s"%s",' % (indent_prop_arg, value))
            lines.append("%s}" % indent_prop)

        return lines

    def build_commands_property(self, dirs_from, to, command, files="*", stage="", IndentLevel=0):
        indent_prop = ''.join(["    "] * IndentLevel)
        indent_prop_arg = ''.join(["    "] * (IndentLevel + 1))
        lines = []

        if command not in ["copy"]:
            return lines

        # make sure we end the ratget dir with a slash
        to = normpath(to) + "/"

        if dirs_from:
            lines.append("%s%scommands{" % (indent_prop, stage))
            for dir_from in dirs_from:
                dir_from = normpath(dir_from).replace("\\", "/")
                # For the 'copy' command
                if command == "copy":
                    lines.append('%s\'{COPY} "%s/%s" "%s"\',' % (indent_prop_arg, dir_from, files, to))
            lines.append("%s}" % indent_prop)

        return lines


    def build_property_group(self, deps):

        indentation = 0

        lines = []
        lines += self.build_property(".Defines", deps.defines, False, IndentLevel=indentation)
        lines += self.build_property(".IncludeDirs", deps.includedirs, True, IndentLevel=indentation)
        lines += self.build_property(".LibDirs", deps.libdirs, True, IndentLevel=indentation)
        lines += self.build_property(".Libs", deps.links, False, IndentLevel=indentation)
        lines += self.build_property(".BinDirs", deps.bindirs, True, IndentLevel=indentation)

        return lines

    def build_conan_module(self, deps):

        lines = []
        lines += self.build_property_group(deps)
        debug_lines = list(lines)
        release_lines = list(lines)

        # Debug properties
        if deps.debug:
            debug_lines += self.build_property_group(deps.debug)
        debug_properties = "\n    ".join(debug_lines)
        self.append(conan_fastbuild_module_with_config.format(name=self.name, config="Debug", properties=debug_properties))

        # Release properties
        if deps.release:
            release_lines += self.build_property_group(deps.release)
        release_properties = "\n    ".join(release_lines)
        self.append(conan_fastbuild_module_with_config.format(name=self.name, config="Release", properties=release_properties))

        # Result
        return True

    def build(self, deps):
        if self.build_conan_module(deps):
            return '\n'.join(self.lines)
        return ''

class fastbuild(Generator):
    @property
    def filename(self):
        return "conan.bff"

    @property
    def content(self):
        sections = ["; Generated Conan file"]
        sections.append(conan_fastbuild_header)

        for dep_name, dep_cpp_info in self.deps_build_info.dependencies:
            deps = FASTBuildDependencies(dep_cpp_info)
            if deps.has_cpp_info():
                module = FASTBuildModule(dep_name)
                sections.append(module.build(deps))

        return "\n".join(sections)

class fastbuild_multi(Generator):
    @property
    def filename(self):
        return "conan.bff"

    @property
    def content(self):
        sections = ["; Generated Conan file"]
        sections.append(conan_fastbuild_header_with_config)

        for dep_name, dep_cpp_info in self.deps_build_info.dependencies:
            deps = FASTBuildDependencies(dep_cpp_info)
            if deps.has_cpp_info():
                module = FASTBuildModuleMultiConfig(dep_name)
                sections.append(module.build(deps))

        return "\n".join(sections)


# The package description
class FASTBuildGeneratorPackage(ConanFile):
    name = "fastbuild-generator"
    version = "0.3.0"
    license = "MIT"
    url = "https://gitlab.com/iceshard-engine/conan-packages/conan-fastbuild-generator"
    description = "FASTBuild generator for the conan package manager."

    def package(self):
        pass
