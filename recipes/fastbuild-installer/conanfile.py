from conan import ConanFile
from conan.tools.files import get, copy
import os

class FASTBuildInstallerConan(ConanFile):
    name = "fastbuild-installer"
    license = "http://fastbuild.org/docs/license.html"
    description = "FASTBuild is a high performance, open-source build system supporting highly scalable compilation, caching and network distribution."
    url = "http://fastbuild.org/docs/home.html"

    settings = "os"

    def generate(self):
        get(self, **self.conan_data["sources"][str(self.settings.os)][self.version])

    def package(self):
        copy(self, "LICENSE.TXT", src=".", dst=os.path.join(self.package_folder, "LICENSES"))
        copy(self, "FBuild.exe", src=".", dst=self.package_folder, keep_path=False)
        copy(self, "FBuildWorker.exe", src=".", dst=self.package_folder, keep_path=False)
        copy(self, "fbuild", src=".", dst=self.package_folder, keep_path=False)
        copy(self, "fbuildworker", src=".", dst=self.package_folder, keep_path=False)

    def package_info(self):
        self.runenv_info.append_path("PATH", self.package_folder)

        if self.settings.os == "Windows":
            self.runenv_info.define("FBUILD_EXE", os.path.join(self.package_folder, "FBuild.exe"))
            self.runenv_info.define("FBUILDWORKER_EXE", os.path.join(self.package_folder, "FBuildWorker.exe"))
        if self.settings.os == "Linux":
            self.runenv_info.define("FBUILD_EXE", os.path.join(self.package_folder, "fbuild"))
            self.runenv_info.define("FBUILDWORKER_EXE", os.path.join(self.package_folder, "fbuildworker"))
