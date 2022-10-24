# from enum import Enum
from conans import ConanFile, MSBuild, CMake
from conans import tools
from shutil import copyfile

from ice.tools.premake import GenPremake5
from ice.tools.cmake import GenCMake
import os

class IceProperties(object):
    def __init__(self):
        self.build_requires = []

class IceTools(object):
    def validate(self):
        if self.settings.build_type == None:
            raise ConanInvalidConfiguration("Multi configuration builds are no longer supported!")

        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.runtime not in ["MD", "MDd"]:
                raise ConanInvalidConfiguration("Only Dynamic runtimes 'MD' and 'MDd' are supported!")

    def source(self):
        source_folder = self._ice.source_dir_templ.format(name=self.name, version=self.version)
        self._ice.source_dir = source_folder

        source_info = self.conan_data["sources"][self.ice_source_key(self.version)]
        if "branch" in source_info:
            git = tools.Git(folder=self._ice.source_dir)
            git.clone(source_info["url"], source_info["branch"])
            if "commit" in source_info:
                git.checkout(source_info["commit"])
        elif "tag" in source_info:
            git = tools.Git(folder=self._ice.source_dir)
            git.clone(source_info["url"], source_info["tag"])
        else:
            tools.get(**source_info)

    def build(self):
        source_folder = self._ice.source_dir_templ.format(name=self.name, version=self.version)
        self._ice.source_dir = os.path.join(self.build_folder, source_folder)
        self._ice.build_dir = self._ice.source_dir

        if self._ice.generator_name == "cmake":
            self._ice.build_dir = os.path.join(self.build_folder, "build")

        with tools.chdir(self._ice.source_dir):

            # Copy premake5 files
            if self._ice.generator_name == "premake5":
                copyfile("../premake5.lua", "premake5.lua")
                if hasattr(self, 'generators') and "premake" in self.generators:
                    copyfile("../conan.lua", "conan.lua")

            self.ice_build()

    def package(self):
        source_folder = self._ice.source_dir_templ.format(name=self.name, version=self.version)
        self._ice.source_dir = os.path.join(self.build_folder, source_folder)
        self._ice.build_dir = self._ice.source_dir

        if self._ice.generator_name == "cmake":
            self._ice.build_dir = os.path.join(self.build_folder, "build")

        self.ice_package()

    # Iceshard method implementations
    def ice_init(self, generator):
        self._ice = IceProperties()

        self._ice.source_dir_templ = "{name}-{version}"
        if hasattr(self, 'source_dir'):
            self._ice.source_dir_templ = self.source_dir

        if generator == None:
            self._ice.generator_name = "none"

        elif generator == "none":
            self._ice.generator_name = generator

        elif generator == "premake5":
            self._ice.generator_name = generator
            self._ice.generator = GenPremake5(self)
            self._ice.build_requires.append(self._ice.generator.premake_installer)
            if hasattr(self, 'requires') or hasattr(self, 'build_requires'):
                self.generators = "premake"
                self._ice.build_requires.append(self._ice.generator.premake_generator)

        elif generator == "cmake":
            self._ice.generator_name = generator
            self._ice.generator = GenCMake(self)
            self._ice.build_requires.append(self._ice.generator.cmake_installer)
            if hasattr(self, 'requires') or hasattr(self, 'build_requires'):
                self.generators = "cmake"

        else:
            self.output.error("Unknown project generator")

    def ice_source_key(self, version):
        return version

    def ice_apply_patches(self, base_path=None):
        for patch in self.conan_data.get("patches", { }).get(self.ice_source_key(self.version), []):
            tools.patch(base_path=base_path, patch_file="{}/{}".format(self.build_folder, patch["patch_file"]))

    def ice_generate(self):
        self._ice.generator.generate()

    def ice_build(self):
        pass

    def ice_package(self):
        pass

    def ice_run_msbuild(self, solution, build_type=None):
        if build_type == None:
            build_type = self.settings.build_type

        msbuild = MSBuild(self)
        msbuild.build(solution, build_type=build_type)

    def ice_run_cmake(self, definitions={}, target=None, build_type=None, build_folder=None):
        if build_type == None:
            build_type = self.settings.build_type
        if build_folder == None:
            build_folder = self._ice.build_dir

        cmake = CMake(self, build_type=build_type)
        for name, value in definitions.items():
            cmake.definitions[name] = value
        cmake.configure(source_folder=self._ice.source_dir, build_folder=build_folder)
        cmake.build(target=target)

    def ice_run_make(self, target=None, build_type=None):
        if build_type == None:
            build_type = self.settings.build_type

        self.run("make -f Makefile config={} {}".format(str(build_type).lower(), "" if target == None else target))

##
## Conan package class.
class ConanIceshardTools(ConanFile):
    name = "conan-iceshard-tools"
    version = "0.8.2"

    exports = "ice/*"
