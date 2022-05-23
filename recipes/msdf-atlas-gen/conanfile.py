from conans import ConanFile, Meson, tools
import os

class MsdfAtlasGenConanRecipe(ConanFile):
    name = "msdf-atlas-gen"
    license = "MIT"
    description = "MSDF font atlas generator."
    url = "https://github.com/Chlumsky/msdf-atlas-gen"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = {
        "fPIC":[True, False],
    }
    default_options = {
        "fPIC": True
    }

    # source_dir = "{name}-{version}"

    # Additional files to export
    exports_sources = ["patches/*"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.8.2@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    requires = "msdfgen/1.9.2@iceshard/stable"

    # Initialize the package
    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires
        # self.build_requires = "meson/0.62.1" # self._ice.build_requires

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def ice_build(self):
        self.run("cd artery-font-format && git submodule update --init")

        self.ice_generate()
        self.ice_apply_patches()

        definitions = { }
        definitions['MSDF_ATLAS_GEN_BUILD_STANDALONE'] = False
        definitions['MSDF_ATLAS_GEN_MSDFGEN_EXTERNAL'] = True
        self.ice_run_cmake(definitions)

    def ice_package(self):
        self.copy("LICENSE.txt", src=self._ice.source_dir, dst="LICENSE")

        self.copy("*.h*", "include/msdfgen/core", src="{}/core".format(self._ice.source_dir), keep_path=True)
        self.copy("*.h*", "include/msdfgen/ext", src="{}/ext".format(self._ice.source_dir), keep_path=True)
        self.copy("*.h*", "include/msdfgen/skia", src="{}/skia".format(self._ice.source_dir), keep_path=True)
        self.copy("msdfgen.h", "include/msdfgen", src="{}".format(self._ice.source_dir), keep_path=True)
        self.copy("msdfgen-*.h", "include/msdfgen", src="{}".format(self._ice.source_dir), keep_path=True)

        build_dir = self._ice.build_dir
        if self.settings.os == "Windows":
            build_dir = os.path.join(build_dir, "../build")

            self.copy("*.lib", dst="lib", src="{}/lib".format(build_dir), keep_path=False)
            self.copy("*.pdb", dst="lib", src="{}/lib".format(build_dir), keep_path=False)
        if self.settings.os == "Linux":
            self.copy("*.a", dst="lib", src="{}/lib".format(build_dir), keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.libs = ['msdfgen-core', 'msdfgen-ext']
