# import os
# from conans import ConanFile, tools, CMake
# from conans.errors import ConanException

from conan import ConanFile

class ZLibConan(ConanFile):
    name = "zlib"
    url = "https://github.com/iceshard-engine/conan-zlib"
    homepage = "https://zlib.net"
    license = "Zlib"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                   "(Also Free, Not to Mention Unencumbered by Patents)")

    settings = "os", "arch", "compiler", "build_type"

    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    python_requires = "conan-iceshard-tools/0.9.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "cmake"

    def ice_build(self):
        self.ice_run_cmake()

    def ice_package_sources(self):
        self.ice_copy("LICENSE", src=".", dst="LICENSES")
        self.ice_copy("zlib.h", src=".", dst="include", keep_path=False)

    def ice_package_artifacts(self):
        self.ice_copy("zconf.h", src=".", dst="include", keep_path=False)

        self.ice_copy("*.dylib", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.so", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.dll", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)

    def package_info(self):
        lib_suffix = "d" if self.settings.build_type == "Debug" else ""

        self.cpp_info.set_property("cmake_file_name", "ZLIB")
        self.cpp_info.set_property("cmake_target_name", "ZLIB")
        self.cpp_info.set_property("cmake_find_package", "ZLIB")

        self.cpp_info.includedirs = [ 'include' ]
        self.cpp_info.libdirs = [ 'lib' ]
        self.cpp_info.libdirs.append("bin") if self.settings.os == "Linux"

        self.cpp_info.libs = [ 'zlib' + lib_suffix ]
