from conan import ConanFile
from conan.tools.microsoft import NMakeDeps, NMakeToolchain
from conan.tools.gnu import MakeDeps #, MakeToolchain
from conan.tools.files import copy, chdir, replace_in_file

import os

class LuaFilesystemConan(ConanFile):
    name = "lua-filesystem"
    license = "MIT"
    description = "LuaFileSystem is a Lua library developed to complement the set of functions related to file systems offered by the standard Lua distribution."
    url = "http://keplerproject.github.io/luafilesystem/"

    settings = "os", "build_type", "compiler", "arch"

    options = { "shared": [True, False] }
    default_options = { "shared":True }

    requires = "lua/5.1.5@iceshard/stable"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "none"
    ice_toolchain = "none"

    def layout(self):
        self.ice_layout("none")
        self.folders.build = self.folders.source

    def generate(self):
        if self.settings.os == "Windows":
            deps = NMakeDeps(self)
            deps_vars = deps.vars()

            tc = NMakeToolchain(self)
            env = tc.environment()
            env.append('CFLAGS', deps_vars.get('CL'))
            env.define('LUA_LIB', deps_vars.get('_LINK_'))
            env.define('LIB', deps_vars.get('LIB'))
            tc.generate(env)

            chdir(self, self.source_folder)
            replace_in_file(self, os.path.join(self.source_folder, "Makefile.win"), "include config.win", "#test")
        else:
            deps = MakeDeps(self)
            deps.generate()

            copy(self, "conandeps.mk", src=".", dst=self.source_folder)

            # Update config file to use conan provided paths and values
            path_config = os.path.join(self.source_folder, "config")
            replace_in_file(self, path_config, "PREFIX=", "include {}\nPREFIX=".format('conandeps.mk'))
            replace_in_file(self, path_config, "$(LUA_INC)", "-I$(CONAN_INCLUDE_DIRS)")
            replace_in_file(self, path_config, "gcc", str(self.settings.compiler))

            # Update Makefile to use conan provided paths and values
            path_makefile = os.path.join(self.source_folder, "Makefile")
            replace_in_file(self, path_makefile, "$(LUA_LIBDIR)", "-L$(CONAN_LIB_DIRS)")


    def ice_build(self):
        if self.settings.os == "Windows":
            chdir(self, self.build_folder)
            self.run("nmake /f Makefile.win")
        else:
            self.run("make")

    def ice_package_sources(self):
        self.ice_copy("LICENSE", src=".", dst="LICENSES")
        self.ice_copy("*.h", src="src", dst="include", keep_path=False)

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.dll", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.so", src=".", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.includedirs = [ "include" ]
        self.cpp_info.libs = [ "lfs" ]

        # Enviroment info
        if self.settings.os == "Windows":
            self.runenv_info.append("LUA_CPATH", os.path.join(self.package_folder, "bin/?.dll"), separator=';')
        if self.settings.os == "Linux":
            self.runenv_info.append("LUA_CPATH", os.path.join(self.package_folder, "lib/lib?.so"), separator=';')
