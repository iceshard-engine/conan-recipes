from conans import ConanFile, tools
import os

class PremakeInstallerConan(ConanFile):
    name = "premake-installer"
    license = "https://github.com/premake/premake-core/blob/master/LICENSE.txt"
    description = "Premake is a command line utility which reads a scripted definition of a software project."
    url = "https://premake.github.io/index.html"

    settings = "os"

    def source(self):
        source_info = self.conan_data["sources"][str(self.settings.os)][self.version]
        if source_info != None:
            tools.get(**source_info)

    def package(self):
        self.copy("LICENSE.txt", dst="LICENSE")
        if self.settings.os == "Windows":
            self.copy("premake5.exe", keep_path=False)
        if self.settings.os == "Linux":
            self.copy("premake5", keep_path=False)

    def package_info(self):
        self.env_info.path.append(self.package_folder)
