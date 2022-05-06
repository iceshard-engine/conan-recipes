from conans import ConanFile, tools
import os

class BrotliConanRecipe(ConanFile):
    name = "brotli"
    license = "MIT"
    description = "Brotli compression format."
    url = "https://github.com/google/brotli"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = {
      "fPIC":[True, False],
      "shared":[True, False]
    }
    default_options = {
      "fPIC": True,
      "shared": False
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
        self.info.options.shared = "Any"

    def ice_build(self):
      definitions = {}
      definitions['BROTLI_BUNDLED_MODE'] = True
      definitions['BROTLI_DISABLE_TESTS'] = True
      self.ice_run_cmake()

    def ice_package(self):
        self.copy("LICENSE", src=self._ice.source_dir, dst="LICENSE/")

        self.copy("*.h", "include/", src="{}/c/include".format(self._ice.source_dir), keep_path=True)

        build_dir = os.path.normpath(self._ice.build_dir + "/../build")
        build_type = self.settings.build_type

        if self.settings.os == "Windows":
            lib_names = ['brotlicommon', 'brotlienc', 'brotlidec']
            for lib in lib_names:
                self.copy(lib + ".dll", dst="bin", src="{}/{}".format(build_dir, build_type), keep_path=False)
                self.copy(lib + ".pdb", dst="bin", src="{}/{}".format(build_dir, build_type), keep_path=False)
                self.copy(lib + ".lib", dst="lib", src="{}/{}".format(build_dir, build_type), keep_path=False)

                self.copy(lib + "-static.lib", dst="lib", src="{}/{}".format(build_dir, build_type), keep_path=False)
                self.copy(lib + "-static.pdb", dst="lib", src="{}/{}".format(build_dir, build_type), keep_path=False)

        if self.settings.os == "Linux":
            self.output.error("not implemented")
            # self.copy("*.a", dst="lib", src="{}/{}".format(build_dir, build_type), keep_path=False)
            # self.copy("*.so", dst="bin", src="{}/{}".format(build_dir, build_type), keep_path=False)


    def package_info(self):
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.libs = ['brotli']

        if self.options.shared == True:
            self.cpp_info.bindirs = ['bin']

            if self.settings.os == 'Linux':
                self.cpp_info.libdirs.append('bin')
