from conan import ConanFile
from conan.tools.files import copy, download, get

class PremakeInstallerConan(ConanFile):
    name = "premake-installer"
    license = "https://github.com/premake/premake-core/blob/master/LICENSE.txt"
    description = "Premake is a command line utility which reads a scripted definition of a software project."
    url = "https://premake.github.io/index.html"

    settings = "os"

    def validate(self):
        self.platform = str(self.settings.os)

    def source(self):
        download(self, self.conan_data["sources"][self.version]["license"], "LICENSE.txt")

        source_info = self.conan_data["sources"][self.version][self.platform]
        if source_info != None:
            get(self, **source_info)

    def package(self):
        copy(self, "LICENSE.txt", src=self.build_folder, dst=self.package_folder)

        if self.settings.os == "Windows":
            copy(self, "premake5.exe", src=self.build_folder, dst=self.package_folder, keep_path=False)
        if self.settings.os == "Linux":
            copy(self, "premake5", src=self.build_folder, dst=self.package_folder, keep_path=False)
        if self.settings.os == "Macos":
            copy(self, "premake5", src=self.build_folder, dst=self.package_folder, keep_path=False)

    def package_info(self):
        self.env_info.path.append(self.package_folder)
