# from enum import Enum
from conan import ConanFile
from conan import tools
from conan.tools.scm import Git
from conan.tools.files import chdir, copy, get, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.microsoft import MSBuildToolchain, MSBuild, msvs_toolset
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from os.path import join

import os
import types

class IceProperties(object):
    def __init__(self):
        self.build_requires = []

class IceTools(object):
    def init(self):
        toolchain = None
        if self.ice_toolchain != None:
            toolchain = self.ice_toolchain
        elif self.ice_generator == "cmake":
            toolchain = "cmake"
        elif self.ice_generator == "premake5":
            toolchain = "native"
        else:
            toolchain = "none"

        self.ice_init(self.ice_generator or "none", toolchain)

    def build_requirements(self):
        if self._ice.toolchain_name == "ninja":
            self.tool_requires("ninja/[>=1.11.1 <2.0]")

        if self._ice.generator_name == "cmake":
            self.tool_requires("cmake/[>=3.25.3 <4.0]")
        if self._ice.generator_name == "premake5":
            self.tool_requires("premake-installer/5.0.0@iceshard/stable")
            self.python_requires["premake-generator"]

    def validate(self):
        if self.settings.build_type == None:
            raise ConanInvalidConfiguration("Multi configuration builds are no longer supported!")

        if self.settings.compiler == "msvc":
            if self.settings.compiler.runtime not in ["dynamic", None]:
                raise ConanInvalidConfiguration("Only Dynamic runtimes 'MD' and 'MDd' are supported!")

    def layout(self):
        self.ice_layout()

    def source(self):
        self.ice_source()

    def generate(self):
        self.ice_generate()

    def build(self):
        self.ice_build()

    def package(self):
        # Calls 'ice_package_sources' with a specialized copy method
        if chdir(self, self.source_folder):
            def CopyFromSource(self, pattern, src, dst, excludes=None, keep_path=False):
                copy(self, pattern, src=join(self.source_folder, src), dst=join(self.package_folder, dst), excludes=excludes, keep_path=keep_path)
            self.ice_copy = types.MethodType(CopyFromSource, self)
            self.ice_package_sources()
            del self.ice_copy
        else:
            self.output.error("Failed to enter source folder!")

        # Calls 'ice_package_artifacts' with a specialized copy method
        if chdir(self, self.build_folder):
            def CopyFromBuild(self, pattern, src, dst, excludes=None, keep_path=False):
                copy(self, pattern, src=join(self.build_folder, src), dst=join(self.package_folder, dst), excludes=excludes, keep_path=keep_path)
            self.ice_copy = types.MethodType(CopyFromBuild, self)
            self.ice_package_artifacts()
            del self.ice_copy
        else:
            self.output.error("Failed to enter build folder!")

    # Iceshard method implementations
    def _ice_final_toolchain(self):
        if self.ice_toolchain == "native":
            if self.settings.compiler == "msvc":
                return "msbuild"
            else:
                return "makefile"
        else:
            return self.ice_toolchain

    def ice_init(self, generator, toolchain):
        self._ice = IceProperties()
        self._ice.toolchain_name = toolchain

        # Set the generator name if it's known
        if generator == None or generator == "none":
            self._ice.generator_name = "none"
        elif generator == "premake5":
            self._ice.generator_name = generator
        elif generator == "cmake":
            self._ice.generator_name = generator
        else:
            self.output.error("Unknown project generator")

    def ice_layout(self, generator=None):
        if generator == None:
            generator = self._ice.generator_name

        if generator == "cmake":
            cmake_layout(self)
        else:
            basic_layout(self)

        # Override some specific folders
        self.folders.source = "{}-{}".format(self.name, self.version)

        if generator == "premake5":
            self.folders.generators = self.folders.source
            self.folders.build = self.folders.source

    def ice_source_key(self, version):
        return version

    def ice_apply_patches(self):
        apply_conandata_patches(self)

        # for patch in self.conan_data.get("patches", { }).get(self.ice_source_key(self.version), []):
            # tools.patch(base_path=base_path, patch_file="{}/{}".format(self.build_folder, patch["patch_file"]))

    def ice_source(self):
        source_info = self.conan_data["sources"][self.ice_source_key(self.version)]
        if "branch" in source_info:
            git = Git(self)
            git.clone(source_info["url"], target=".")
            git.checkout(source_info["branch"])
            if "commit" in source_info:
                git.checkout(source_info["commit"])
        elif "tag" in source_info:
            git = Git(self)
            git.clone(source_info["url"], target=".")
            git.checkout(source_info["tag"])
        else:
            get(self, **source_info)

        # Apply patches if any
        self.ice_apply_patches()

    def ice_generate(self, generator=None, toolchain=None):
        if generator == None:
            generator = self._ice.generator_name
        if toolchain == None:
            toolchain = self._ice_final_toolchain()

        if generator == "cmake":
            # TODO: assert toolchain == 'cmake'

            if toolchain == "ninja":
                toolchain = CMakeToolchain(self, "Ninja")
            else:
                toolchain = CMakeToolchain(self)
            deps = CMakeDeps(self)

            self.ice_generate_cmake(toolchain, deps)

            toolchain.generate()
            deps.generate()

        if generator == "premake5":
            PremakeDeps = self.python_requires["premake-generator"].module.PremakeDeps
            deps = PremakeDeps(self)
            self.ice_generate_premake(deps)
            deps.generate()

            # Generates premake5 binary env
            ms = VirtualBuildEnv(self)
            ms.vars().save_script('iceshard_tools')

            premake_generators_vstudio = {
                "11": "vs2012",
                "12": "vs2013",
                "14": "vs2015",
                "15": "vs2017",
                "16": "vs2019",
                "17": "vs2022",
            }

            # Build commandline arguments
            premake_action = "gmake2"
            if self.settings.compiler == "msvc":
                premake_action = premake_generators_vstudio.get(str(self.settings.compiler.version), "vs2022")

            premake_commandline = "premake5 {} --file={}".format(premake_action, join(self.source_folder, "premake5.lua"))
            premake_commandline += " --arch={}".format(self.settings.arch)
            for key, value in self.options.items():
                if value == 'True':
                    premake_commandline += " --{}".format(key)
                elif value != 'False':
                    premake_commandline += " --{}={}".format(key, value)

            # Generate premake5 projects
            self.run(premake_commandline, env=['iceshard_tools'])

        if toolchain == "msbuild":
            toolchain = MSBuildToolchain(self)
            self.ice_toolchain_msbuild(toolchain)
            toolchain.generate()

    def ice_build(self, toolchain=None):
        pass

    ##
    # Specific generator functions
    ##
    def ice_generate_cmake(self, toolchain, deps):
        pass
    def ice_generate_premake(self, deps):
        pass
    def ice_toolchain_msbuild(self, deps):
        pass

    ##
    # Called by IceTools when packagin sources and artifacts
    ##
    def ice_package_sources(self):
        pass

    def ice_package_artifacts(self):
        pass

    ##
    # Methods used to call build systems
    ##
    def ice_run_msbuild(self, solution, target=None, retarget=False):
        msbuild_platforms = {
            "x86": "Win32",
            "x86_64": "x64",
        }

        cmdline = "msbuild {} /p:Configuration={} /p:Platform={}".format(solution, self.settings.build_type, msbuild_platforms.get(str(self.settings.arch), None))
        if target != None:
            cmdline += " /target:{}".format(target)
        if retarget:
            cmdline += " /p:PlatformToolset={}".format(msvs_toolset(self))
        self.run(cmdline)
        # msbuild = MSBuild(self)
        # msbuild.build(solution, targets=targets)

    def ice_run_cmake(self, variables=[], target=None):
        cmake = CMake(self)
        cmake.configure(variables=variables)
        cmake.build(target=target)

    def ice_run_make(self, target=None, build_type=None):
        if build_type == None:
            build_type = self.settings.build_type

        self.run("make -f Makefile config={} {}".format(str(build_type).lower(), "" if target == None else target), env=[])

##
## Conan package class.
class ConanIceshardTools(ConanFile):
    name = "conan-iceshard-tools"
    version = "0.9.1"
    user = "iceshard"
    channel = "stable"
