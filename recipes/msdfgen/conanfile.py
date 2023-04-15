from conan import ConanFile

class MsdfGenConanRecipe(ConanFile):
    name = "msdfgen"
    license = "MIT"
    description = "Multi-channel signed distance field generator."
    url = "https://github.com/Chlumsky/msdfgen"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = {
        "fPIC":[True, False]
    }
    default_options = {
        "fPIC": True,
    }

    requires = "freetype/2.12.1@iceshard/stable"

    # Additional files to export
    exports_sources = ["patches/*", "Findmsdfgen.cmake"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.9.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "cmake"

    def configure(self):
        if self.settings.compiler == 'msvc':
            del self.options.fPIC

    def ice_generate_cmake(self, toolchain, deps):
        toolchain.variables['MSDFGEN_BUILD_STANDALONE'] = False
        toolchain.variables['MSDFGEN_INSTALL'] = False

    def ice_build(self):
        self.ice_run_cmake()

    def ice_package_sources(self):
        self.ice_copy("LICENSE.txt", src=".", dst="LICENSE")

        self.ice_copy("*.h*", src="core", dst="include/msdfgen/core", keep_path=True)
        self.ice_copy("*.h*", src = "ext", dst="include/msdfgen/ext", keep_path=True)
        self.ice_copy("*.h*", src="skia", dst="include/msdfgen/skia", keep_path=True)
        self.ice_copy("*.h*", src="include", dst="include/msdfgen/include", keep_path=True)
        self.ice_copy("msdfgen.h", src=".", dst="include/msdfgen", keep_path=True)
        self.ice_copy("msdfgen-*.h", src=".", dst="include/msdfgen", keep_path=True)

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "msdfgen")
        self.cpp_info.set_property("cmake_target_name", "msdfgen::msdfgen")

        self.cpp_info.includedirs = ['include', 'include/msdfgen']

        self.cpp_info.libdirs = ['lib']
        self.cpp_info.libs = ['msdfgen-core', 'msdfgen-ext']
