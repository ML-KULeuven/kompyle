cmake_minimum_required(VERSION 3.15...3.27)
project(kompyle LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
# -----------------------------------------------
# DEPENDENCIES 
# -----------------------------------------------

find_package(Python 3.10
        REQUIRED COMPONENTS Interpreter Development.Module
        OPTIONAL_COMPONENTS Development.SABIModule)

find_package(nanobind       CONFIG REQUIRED)

find_package(cryptominisat5 MODULE REQUIRED)
find_package(arjun          MODULE REQUIRED)
find_package(ganak          MODULE REQUIRED)
find_package(sbva           CONFIG REQUIRED)
find_package(breakid        CONFIG REQUIRED)
find_package(approxmc       CONFIG REQUIRED)
find_package(klay           CONFIG REQUIRED)
find_package(sdd            CONFIG REQUIRED)

find_package(cadical        MODULE REQUIRED)
find_package(cadiback       MODULE REQUIRED)


# -----------------------------------------------
# LIBRARY KOMPYLE
# -----------------------------------------------

set(dependencies
        klay
        cryptominisat5
        arjun
        ganak
        sbva
        breakid
        approxmc
        sdd::sdd
        sdd::sdd_compiler
        cadical::cadical
        cadiback::cadiback
)

add_library(kompyle SHARED
  src/core.cpp
  src/sdd.cpp
)

target_include_directories(kompyle
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)


target_link_libraries(kompyle PUBLIC ${dependencies}
)

# NOTE(Ibrahim):
# * all these shared libs are packed together in kompyle site-package
# as you can see, we bundle klay together as well, duplicate because 
# we also install a python package klay. It is easier than to link
# because of macos... and python packages needing to be self-contained
foreach(lib ${dependencies})
    get_target_property(lib_loc ${lib} LOCATION)
    install(FILES ${lib_loc} DESTINATION ${SKBUILD_PLATLIB_DIR}/kompyle)
endforeach()

set(RPATH_ORIGIN "$ORIGIN")
if(APPLE)
  set(RPATH_ORIGIN "@loader_path")
endif()

set_target_properties(kompyle PROPERTIES
    INSTALL_RPATH "${RPATH_ORIGIN}"
)

# NOTE(Ibrahim):
# puts kompyle.abi3.so into the kompyle/ Python package directory
# (inside the wheel)
# also install (lib)kompyle in Python pakcage directory
# which isn't needed if installed system wide
install(TARGETS kompyle LIBRARY DESTINATION kompyle)

# -----------------------------------------------
# PYTHON KOMPYLE EXTENSION
# -----------------------------------------------

nanobind_add_module(pkompyle
  STABLE_ABI
  NOMINSIZE
  NB_STATIC
  src/core_bindings.cpp
)

target_link_libraries(pkompyle PRIVATE kompyle klay)

# NOTE(Ibrahim):
# sketchy, but if installed system wide, this wouldn't be necssary...
set_target_properties(pkompyle PROPERTIES
    INSTALL_RPATH "${RPATH_ORIGIN}"
)

# NOTE(Ibrahim):
# puts pkompyle.abi3.so into the kompyle/ Python package directory
# (inside the wheel)
install(TARGETS pkompyle LIBRARY DESTINATION kompyle)

# -----------------------------------------------
# PYTHON KOMPYLE EXTENSION STUBS
# -----------------------------------------------
#
# # https://nanobind.readthedocs.io/en/latest/typing.html#cmake-interface
# nanobind_add_stub(
#   pkompyle_stub
#   MODULE pkompyle
#   OUTPUT pkompyle.pyi
#   PYTHON_PATH $<TARGET_FILE_DIR:pkompyle>
#   DEPENDS pkompyle
# )
#
# install(FILES
#   "${CMAKE_CURRENT_BINARY_DIR}/pkompyle.pyi"
#   DESTINATION kompyle
# )
