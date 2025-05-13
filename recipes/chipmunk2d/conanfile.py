from conan import ConanFile

class Chipmunk2DConan(ConanFile):
    name = "chipmunk2d"
    license = "MIT"
    description = "A fast and lightweight 2D game physics library."
    url = "https://github.com/slembcke/Chipmunk2D"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = { "shared":[True, False], "fPIC":[True,False] }
    default_options = { "shared":False, "fPIC":True }

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "ninja"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def ice_build(self):
        variables = { }
        variables['BUILD_DEMOS'] = False
        variables['BUILD_SHARED'] = self.options.shared
        variables['BUILD_STATIC'] = not self.options.shared

        # We don't want to install anything
        variables['INSTALL_DEMOS'] = False
        variables['INSTALL_STATIC'] = False
        if self.settings.os != "Windows":
            variables['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        self.ice_run_cmake(variables=variables)

    def ice_package_sources(self):
        self.ice_copy("LICENSE.txt", src=".", dst="LICENSES")
        self.ice_copy("*.h", src="include", dst="include", keep_path=True)

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.dll", src=".", dst="bin", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.so*", src=".", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        if self.settings.os != "Windows":
            self.cpp_info.libdirs.append("bin")

        self.cpp_info.libs = ["chipmunk"]
