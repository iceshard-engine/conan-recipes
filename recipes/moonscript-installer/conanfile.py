from conans import ConanFile, MSBuild, tools
from shutil import copyfile
import os

class MoonscriptInstallerConan(ConanFile):
    name = "moonscript-installer"
    version = "0.5.0"
    license = "MIT"
    description = "Installer for the moonscript wrapper for lua. Provides the moon and moonc commane line tools."
    url = "https://github.com/leafo/moonscript"

    settings = "os"

    requires = [
        "lua/5.1.5@iceshard/stable",
        "lua-filesystem/1.8.0@iceshard/stable",
        "lua-lpeg/0.12.0@iceshard/stable"
    ]

    # Additional exports
    exports_sources = [
        "bin/moon.bat",
        "bin/moonc.bat",
        "bin/moon.sh",
        "bin/moonc.sh",
        "bin/moon_unix",
        "bin/moonc_unix",
        "bin/moon_windows",
    ]

    folder_names = {
        "moonscript": "moonscript-source",
        "alt-getopt": "alt-getopt-source",
        "argparse": "argparse-source",
        "jsonlua": "jsonlua-source",
    }

    def build_id(self):
        del self.info_build.settings.os

    def package_id(self):
        del self.info.settings.os

    def source(self):
        source_info = self.conan_data["sources"][self.version]
        if source_info != None:

            for dep, info in source_info.items():
                git = tools.Git(folder=self.folder_names[dep])
                git.clone(info['url'])
                if "commit" in info:
                    git.checkout(info['commit'])
                elif "tag" in info:
                    git.checkout(info['tag'])


    # Export the files available in the package
    def package(self):
        # Additonal batch files to copy
        self.copy("*.*", src="bin", dst="scripts/moonscript/bin", keep_path=False)

        for name, folder_name in self.folder_names.items():
            if name == "moonscript":
                self.copy("bin/*", src=folder_name, dst="scripts/moonscript", keep_path=True)
                self.copy("moon/*", src=folder_name, dst="scripts/moonscript", keep_path=True)
                self.copy("moonscript/*", src=folder_name, dst="scripts/moonscript", keep_path=True)
            else:
                self.copy("LICENSE", src=folder_name, dst="LICENSE-{}".format(name))
                self.copy("*.lua", src=folder_name, dst="scripts/{}".format(name), keep_path=False)

        copyfile("bin/moon_unix", "bin/moon")
        copyfile("bin/moonc_unix", "bin/moonc")
        self.copy("moon", src="bin", dst="scripts/moonscript/bin", keep_path=False)
        self.copy("moonc", src="bin", dst="scripts/moonscript/bin", keep_path=False)
        self.copy("moon_windows", src="bin", dst="scripts/moonscript/bin", keep_path=False)


    def package_info(self):
        # Enviroment info
        self.env_info.PATH.append(os.path.join(self.package_folder, "scripts/moonscript/bin"))

        if self.settings.os == "Linux":
            self.env_info.MOON_SCRIPT = os.path.join(self.package_folder, "scripts/moonscript/bin/moon")
            self.env_info.MOONC_SCRIPT = os.path.join(self.package_folder, "scripts/moonscript/bin/moonc")

        elif self.settings.os == "Windows":
            self.env_info.MOON_SCRIPT = os.path.join(self.package_folder, "scripts/moonscript/bin/moon.bat")
            self.env_info.MOONC_SCRIPT = os.path.join(self.package_folder, "scripts/moonscript/bin/moonc.bat")

        # Lua paths info
        for name in self.folder_names:
            self.env_info.LUA_PATH.append(os.path.join(self.package_folder, "scripts/{}/?.lua".format(name)))

        # Extra entry
        self.env_info.LUA_PATH.append(os.path.join(self.package_folder, "scripts/moonscript/?/init.lua"))
