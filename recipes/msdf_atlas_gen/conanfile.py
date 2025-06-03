from conan import ConanFile

class MsdfAtlasGenConanRecipe(ConanFile):
    name = "msdf_atlas_gen"
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

    requires = "msdfgen/1.9.2@iceshard/stable"

    # Additional files to export
    exports_sources = ["patches/*"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.1@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "cmake"

    def configure(self):
        if self.settings.compiler == 'msvc':
            del self.options.fPIC

    def source(self):
        self.ice_source()
        self.run("cd artery-font-format && git submodule update --init")

    def ice_build(self):
        variables = { }
        variables['MSDF_ATLAS_GEN_BUILD_STANDALONE'] = False
        variables['MSDF_ATLAS_GEN_MSDFGEN_EXTERNAL'] = True
        self.ice_run_cmake(variables=variables)

    def ice_package_sources(self):
        self.ice_copy("LICENSE.txt", src=".", dst="LICENSE")
        self.ice_copy("*.h*", src="msdf-atlas-gen", dst="include/msdf-atlas-gen", keep_path=True)

    def ice_package_artifacts(self):
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.includedirs = [
            'include',
            # os.path.join(self.dependencies['msdfgen'].package_folder, "include/msdfgen")
        ]
        self.cpp_info.libs = ['msdf-atlas-gen']
