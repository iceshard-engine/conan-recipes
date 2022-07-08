require "conan"

newoption {
    trigger = "shared",
    description = "Build as shared lib",
}

newoption {
    trigger = "arch",
    description = "Build for the given architecture",
    value = "ARCH"
}

workspace "LuaLPeg"
    configurations { "Debug", "Release" }

    architecture(_OPTIONS.arch)

    filter { "action:vs*" }
        defines { "_CRT_SECURE_NO_WARNINGS" }

    filter { "Release" }
        optimize "On"

    project "lpeg"
        kind(iif(_OPTIONS.shared, "SharedLib", "StaticLib"))
        language "C"

        conan {
            "lua"
        }

        includedirs {
            "src"
        }

        files {
            "*.c", "*.def"
        }
