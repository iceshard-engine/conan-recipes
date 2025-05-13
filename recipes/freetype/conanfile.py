from conan import ConanFile
import os

class FreeTypeConanRecipe(ConanFile):
    name = "freetype"
    description = "FreeType is a freely available software library to render fonts."
    url = "https://github.com/freetype/freetype"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = {
      "fPIC":[True, False]
    }
    default_options = {
      "fPIC": True
    }

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "cmake"

    def configure(self):
        if self.settings.compiler == 'msvc':
            del self.options.fPIC

    def ice_generate_cmake(self, toolchain, deps):
        toolchain.variables['SKIP_INSTALL_ALL'] = True

    def ice_build(self):
        self.ice_run_cmake()

    def ice_package_sources(self):
        self.ice_copy("docs/FTL.TXT", src=".", dst="LICENSES/", keep_path=False)
        self.ice_copy("docs/GPLv2.TXT", src=".", dst="LICENSES/", keep_path=False)
        self.ice_copy("*.h", src="include", dst="include/", keep_path=True)

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Freetype")
        self.cpp_info.set_property("cmake_target_name", "Freetype::Freetype")

        self.cpp_info.libdirs = ['lib']

        if self.settings.build_type == "Debug":
            self.cpp_info.libs = ['freetyped']
        else:
            self.cpp_info.libs = ['freetype']
