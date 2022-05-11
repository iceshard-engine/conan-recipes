from conans import ConanFile, tools
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

    source_dir = "{name}-{version}"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.1@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    # Initialize the package
    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def package_id(self):
        pass

    def ice_build(self):
      definitions = {}
      definitions['SKIP_INSTALL_ALL'] = True
      self.ice_run_cmake(definitions)

    def ice_package(self):
        self.copy("docs/FTL.TXT", src=self._ice.source_dir, dst="LICENSES/")
        self.copy("docs/GPLv2.TXT", src=self._ice.source_dir, dst="LICENSES/")

        self.copy("*.h", "include/", src="{}/include".format(self._ice.source_dir), keep_path=True)

        build_dir = os.path.normpath(self._ice.build_dir + "/../build")
        build_type = self.settings.build_type

        if self.settings.os == "Windows":
            self.copy("*.lib", dst="lib", src="{}/{}".format(build_dir, build_type), keep_path=False)
            self.copy("*.pdb", dst="lib", src="{}/{}".format(build_dir, build_type), keep_path=False)

        if self.settings.os == "Linux":
            self.copy("*.a", dst="lib", src="{}/{}".format(build_dir, build_type), keep_path=False)


    def package_info(self):
        self.cpp_info.libdirs = ['lib']

        if self.settings.build_type == "Debug":
          self.cpp_info.libs = ['freetyped']
        else:
          self.cpp_info.libs = ['freetype']
