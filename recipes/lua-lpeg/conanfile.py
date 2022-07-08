from conans import ConanFile
import os

class LuaLpegConan(ConanFile):
    name = "lua-lpeg"
    license = "MIT"
    description = "lua Lpeg."
    url = "https://github.com/LuaDist/lpeg"

    settings = "os", "build_type", "compiler", "arch"

    options = { "shared": [True, False] }
    default_options = { "shared":True }

    exports_sources = ["premake5.lua", "LICENSE_LPEG.txt"]
    requires = "lua/5.1.5@iceshard/stable"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"


    def init(self):
        self.ice_init("premake5")
        self.build_requires = self._ice.build_requires

    def ice_build(self):
        self.ice_generate()

        if self.settings.compiler == "Visual Studio":
            self.ice_run_msbuild("LuaLPeg.sln")
        else:
            self.ice_run_make()

    def ice_package(self):
        self.copy("LICENSE_LPEG.txt", dst="LICENSES")
        self.copy("*.h", "include", "{}".format(self._ice.source_dir), keep_path=False)

        build_dir = os.path.join(self._ice.build_dir, "bin")
        if self.settings.os == "Windows":
            self.copy("*.lib", "lib", build_dir, keep_path=False)
            self.copy("*.dll", "bin", build_dir, keep_path=False)
        if self.settings.os == "Linux":
            self.copy("*.a", "lib", build_dir, keep_path=False)
            self.copy("*.so", "lib", build_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.includedirs = [ "include" ]
        self.cpp_info.libs = [ "lpeg" ]

        # Enviroment info
        if self.settings.os == "Windows":
            self.env_info.LUA_CPATH.append(os.path.join(self.package_folder, "bin/?.dll"))
        if self.settings.os == "Linux":
            self.env_info.LUA_CPATH.append(os.path.join(self.package_folder, "lib/lib?.so"))
