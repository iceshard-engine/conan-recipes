from conan import ConanFile

class FmtConan(ConanFile):
    name = "fmt"
    license = "MIT"
    description = "{{fmt}} is an open-source formatting library providing a fast and safe alternative to C stdio and C++ iostreams."
    url = "https://fmt.dev/latest/index.html"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = { "fPIC": [True,False] }
    default_options = { "fPIC":True }

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
        variables['FMT_INSTALL'] = False
        variables['FMT_TEST'] = False
        variables['FMT_DOC'] = False
        if self.settings.os != "Windows":
            variables['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        self.ice_run_cmake(variables=variables)

    def ice_package_sources(self):
        self.ice_copy("LICENSE.rst", src=".", dst="LICENSES")
        self.ice_copy("*.h", src="include", dst="include", keep_path=True)

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        if self.settings.build_type == "Release":
            self.cpp_info.libs = ["fmt"]
        else: # self.settings.build_type == "Debug":
            self.cpp_info.libs = ["fmtd"]
