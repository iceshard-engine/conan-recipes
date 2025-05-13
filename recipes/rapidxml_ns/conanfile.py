from conan import ConanFile

class RapidXMLNSConanRecipe(ConanFile):
    name = "rapidxml_ns"
    description = "RapidXML NS library - RapidXML with added XML namespaces support."
    url = "https://github.com/svgpp/rapidxml_ns"

    # Settings and options
    settings = "os", "compiler", "arch", "build_type"

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/1.0.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    ice_generator = "none"
    ice_toolchain = "none"

    def package_id(self):
        self.info.clear()

    def ice_package_sources(self):
        self.ice_copy("LICENSE.txt", src=".", dst="LICENSES")
        self.ice_copy("*.hpp", src=".", dst="include/rapidxml_ns", excludes=("tests/*", "doc/*"))

    def package_info(self):
        self.cpp_info.includedirs = [ "include" ]
