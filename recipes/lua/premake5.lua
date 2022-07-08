newoption {
    trigger = "shared",
    description = "Build as shared lib",
}

newoption {
    trigger = "arch",
    description = "Build for the given architecture",
    value = "ARCH"
}

workspace "Lua"
    configurations { "Debug", "Release" }

    architecture(_OPTIONS.arch)

    filter { "action:vs*" }
        defines { "_CRT_SECURE_NO_WARNINGS" }

    filter { "Release" }
        optimize "On"

    filter { "system:linux", "options:shared" }
        defines { "LUA_USE_POSIX", "LUA_USE_DLOPEN" }
        links { 'dl' }

    filter { "system:windows", "options:shared" }
        defines { "LUA_BUILD_AS_DLL" }

    project "lualib"
        kind(iif(_OPTIONS.shared, "SharedLib", "StaticLib"))
        language "C"

        targetname "lua51"

        includedirs {
            "src"
        }

        files {
            "src/*.c",
            "src/*.def"
        }

        removefiles { "src/luac.c", "src/lua.c", "src/print.c" }

    project "luac"
        kind "ConsoleApp"

        includedirs {
            "src"
        }

        files {
            "src/*.c",
        }

        removefiles {
            "src/lua.c"
        }

    project "lua"
        kind "ConsoleApp"

        includedirs {
            "src"
        }

        links {
            "lualib"
        }

        files {
            "src/lua.c"
        }
