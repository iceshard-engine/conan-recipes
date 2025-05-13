from conan import ConanFile

class CLI11ConanRecipe(ConanFile):
    name = "cli11"
    description = "CLI11 is a command line parser for C++11 and beyond that provides a rich feature set with a simple and intuitive interface."
    url = "https://github.com/CLIUtils/CLI11"
    license = "MIT"

    # Default version, channel and user
    version_default = "2.4.1"
    channel = "stable"
    user = "iceshard"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "none"
    ice_toolchain = "none"

    def set_version(self):
        self.version = self.version or self.version_default

    def package_id(self):
        self.info.clear()

    def ice_package_sources(self):
        self.ice_copy("LICENSE", src=".", dst="LICENSES")
        self.ice_copy("*.hpp", src="include", dst="include", keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = [ "include" ]
