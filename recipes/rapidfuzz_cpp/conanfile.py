from conan import ConanFile
from conan.tools.files import copy, rename
from os.path import join

class RapidFuzzCppConan(ConanFile):
    name = "rapidfuzz_cpp"
    license = "https://github.com/rapidfuzz/rapidfuzz-cpp/blob/main/LICENSE"
    description = "Rapid fuzzy string matching in C++ using the Levenshtein Distance"
    url = "https://github.com/rapidfuzz/rapidfuzz-cpp/tree/main"

    # Setting and options
    settings = "os", "compiler", "arch", "build_type"

    # Default version, channel and user
    version_default = "3.0.5"
    channel = "stable"
    user = "iceshard"

    # Additional files to export
    exports_sources = ["CMakeLists.txt"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.1@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "none"
    ice_toolchain = "none"

    def package_id(self):
        self.info.clear()

    def ice_package_sources(self):
        self.ice_copy("LICENSE", src=".", dst="LICENSES")
        self.ice_copy("*.hpp", src="rapidfuzz", dst="include/rapidfuzz", keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = [ "include" ]

    def set_version(self):
        self.version = self.version or self.version_default
