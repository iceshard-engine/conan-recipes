from conans import ConanFile, tools
import os

class FASTBuildInstallerConan(ConanFile):
    name = "fastbuild-installer"
    license = "http://fastbuild.org/docs/license.html"
    description = "FASTBuild is a high performance, open-source build system supporting highly scalable compilation, caching and network distribution."
    url = "http://fastbuild.org/docs/home.html"

    settings = "os"

    def source(self):
        source_info = self.conan_data["sources"][str(self.settings.os)][self.version]
        if source_info != None:
            tools.get(**source_info)

    def package(self):
        self.copy("LICENSE.TXT", dst="LICENSE")
        if self.settings.os == "Windows":
            self.copy("FBuild.exe", keep_path=False)
            self.copy("FBuildWorker.exe", keep_path=False)
        if self.settings.os == "Linux":
            self.copy("fbuild", keep_path=False)
            self.copy("fbuildworker", keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(self.package_folder)

        if self.settings.os == "Windows":
            self.env_info.FBUILD_EXE = os.path.join(self.package_folder, "FBuild.exe")
            self.env_info.FBUILDWORKER_EXE = os.path.join(self.package_folder, "FBuildWorker.exe")
        if self.settings.os == "Linux":
            self.env_info.FBUILD_EXE = os.path.join(self.package_folder, "fbuild")
            self.env_info.FBUILDWORKER_EXE = os.path.join(self.package_folder, "fbuildworker")
