from conan import ConanFile

class RapidJSONConanRecipe(ConanFile):
    name = "rapidjson"
    description = "A fast JSON parser/generator for C++ with both SAX/DOM style API"
    topics = ("rapidjson", "json", "parser", "generator")
    url = "https://github.com/Tencent/rapidjson"
    homepage = "http://rapidjson.org"
    license = "MIT"

    # Default user and channel
    user = "iceshard"
    channel = "stable"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.1@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "none"
    ice_toolchain = "none"

    def package_id(self):
        self.info.clear()

    def ice_package_sources(self):
        self.ice_copy("license.txt", src=".", dst="LICENSES")
        self.ice_copy("*.h", src="include", dst="include", keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = [ "include" ]
