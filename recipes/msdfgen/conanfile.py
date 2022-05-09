from conans import ConanFile, Meson, tools
import os

class MsdfGenConanRecipe(ConanFile):
    name = "msdfgen"
    license = "MIT"
    description = "Multi-channel signed distance field generator."
    url = "https://github.com/Chlumsky/msdfgen"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = {
        "fPIC":[True, False],
    }
    default_options = {
        "fPIC": True
    }

    source_dir = "{name}-{version}"

    # Additional files to export
    exports_sources = ["patches/*"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    requires = "freetype/2.12.1@iceshard/stable"

    # Initialize the package
    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires
        # self.build_requires = "meson/0.62.1" # self._ice.build_requires

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def ice_build(self):
        self.ice_apply_patches()
        self.ice_run_cmake()

    def ice_package(self):
        self.copy("LICENSE.txt", src=self._ice.source_dir, dst="LICENSE")

        self.copy("*.h*", "include/msdfgen/core", src="{}/core".format(self._ice.source_dir), keep_path=True)
        self.copy("*.h*", "include/msdfgen/ext", src="{}/ext".format(self._ice.source_dir), keep_path=True)
        self.copy("*.h*", "include/msdfgen/skia", src="{}/skia".format(self._ice.source_dir), keep_path=True)
        self.copy("msdfgen.h", "include/msdfgen", src="{}".format(self._ice.source_dir), keep_path=True)
        self.copy("msdfgen-*.h", "include/msdfgen", src="{}".format(self._ice.source_dir), keep_path=True)

        build_dir = self._ice.build_dir
        if self.settings.os == "Windows":
            self.copy("*.lib", dst="lib", src="{}/../build/lib".format(build_dir), keep_path=False)
            self.copy("*.pdb", dst="lib", src="{}/../build/lib".format(build_dir), keep_path=False)
        if self.settings.os == "Linux":
            self.copy("*.a", dst="lib", src="{}/../build/lib".format(build_dir), keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.libs = ['msdfgen-core', 'msdfgen-ext']
