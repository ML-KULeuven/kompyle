cmake_minimum_required(VERSION 3.15...3.27)
project(kompyle LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

if(APPLE)
    set(RPATH_ORIGIN "@loader_path")
else()
    set(RPATH_ORIGIN "$ORIGIN")
endif()

# -----------------------------------------------
# DEPENDENCIES 
# -----------------------------------------------

find_package(Python 3.10
        REQUIRED COMPONENTS Interpreter Development.Module
        OPTIONAL_COMPONENTS Development.SABIModule)

find_package(Boost CONFIG REQUIRED COMPONENTS program_options)

find_package(nanobind       CONFIG REQUIRED)
find_package(klay           CONFIG REQUIRED)

find_package(cryptominisat5 MODULE REQUIRED)
find_package(arjun          MODULE REQUIRED)
find_package(ganak          MODULE REQUIRED)
find_package(sbva           MODULE REQUIRED)
find_package(breakid        MODULE REQUIRED)
find_package(approxmc       MODULE REQUIRED)
find_package(md4            MODULE REQUIRED)

find_package(GMP            MODULE REQUIRED)
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
        sbva::sbva
        breakid::breakid
        approxmc::approxmc
        cadical::cadical
        cadiback::cadiback
        md4::d4
)

add_library(kompyle SHARED
        src/kcircuit.cc
        src/d4/compile.cc
        src/d4/gated_formula.cc
        src/d4/internal.cc
        src/d4/d4_stats.cc
        # src/ganak/circuit_field.cc
        src/ganak/compile.cc
        src/ganak/internal.cc
)

target_include_directories(kompyle
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
            $<INSTALL_INTERFACE:include>
        PRIVATE
            ${CMAKE_SOURCE_DIR}/src
)

target_link_libraries(kompyle
        PUBLIC
            klay
        PRIVATE
            cryptominisat5
            arjun
            ganak
            sbva::sbva
            breakid::breakid
            approxmc::approxmc
            cadical::cadical
            cadiback::cadiback
            md4::d4
            GMP::gmp
            Boost::program_options
)

set_target_properties(kompyle PROPERTIES
    INSTALL_RPATH "${RPATH_ORIGIN}"
    INSTALL_RPATH_USE_LINK_PATH TRUE
)
install(TARGETS kompyle LIBRARY DESTINATION kompyle)

# -----------------------------------------------
# PYTHON KOMPYLE EXTENSION
# -----------------------------------------------

nanobind_add_module(pkompyle
        STABLE_ABI
        NOMINSIZE
        NB_STATIC
        src/python/module.cc
        src/python/circuit_bindings.cc
        src/python/gated_formula_bindings.cc
        src/python/compile_bindings.cc
        src/python/stats_bindings.cc
)

target_include_directories(pkompyle
        PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(pkompyle
        PRIVATE
            kompyle
            klay
)

set_target_properties(pkompyle PROPERTIES
    INSTALL_RPATH "${RPATH_ORIGIN}"
    INSTALL_RPATH_USE_LINK_PATH TRUE
)
install(TARGETS pkompyle LIBRARY DESTINATION kompyle)

# -----------------------------------------------
# PYTHON KOMPYLE EXTENSION STUBS
# -----------------------------------------------

# https://nanobind.readthedocs.io/en/latest/typing.html#cmake-interface
nanobind_add_stub(
  pkompyle_stub
  MODULE pkompyle
  OUTPUT pkompyle.pyi
  PYTHON_PATH $<TARGET_FILE_DIR:pkompyle>
  DEPENDS pkompyle kompyle
)

install(FILES
  "${CMAKE_CURRENT_BINARY_DIR}/pkompyle.pyi"
  DESTINATION kompyle
)
