from conan import ConanFile

class Catch2Conan(ConanFile):
    name = "catch2"
    license = "BSL-1.0 License"
    description = "A modern, C++-native, header-only, test framework for unit-tests, TDD and BDD."
    url = "https://github.com/catchorg/Catch2"

    # Package values
    user = "iceshard"
    channel = "stable"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    options = {"with_main":[True, False]}
    default_options = {"with_main":True}

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.1@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "cmake"
    ice_toolchain = "ninja"

    def package_id(self):
        del self.info.options.with_main

    def ice_generate_cmake(self, toolchain, deps):
        super().ice_generate_cmake(toolchain, deps)

        toolchain.blocks['cppstd'].values = { 'cppstd': '20', 'cppstd_extensions': 'ON' }

    def ice_build(self):
        self.ice_run_cmake()

    def ice_package_sources(self):
        self.ice_copy("LICENSE.txt", src=".", dst="LICENSES")
        self.ice_copy("*.hpp", src="src", dst="include", keep_path=True)

    def ice_package_artifacts(self):
        self.ice_copy("*.hpp", src="generated-includes", dst="include", keep_path=True)
        self.ice_copy("*.lib", src=".", dst="lib", keep_path=False)
        self.ice_copy("*.a", src=".", dst="lib", keep_path=False)

    def package_info(self):
        lib_suffix = "d" if self.settings.build_type == "Debug" else ""

        self.cpp_info.libs = [ "Catch2" + lib_suffix ]
        if self.options.with_main:
            self.cpp_info.libs.append("Catch2Main" + lib_suffix)
        # else: Manual (do nothing, we need to provide it manually)
