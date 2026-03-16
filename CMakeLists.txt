cmake_minimum_required(VERSION 3.15...3.27)
project(kompyle LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# -----------------------------------------------
# DEPENDENCIES 
# -----------------------------------------------

find_package(Python 3.10
        REQUIRED COMPONENTS Interpreter Development.Module
        OPTIONAL_COMPONENTS Development.SABIModule)

find_package(nanobind CONFIG REQUIRED)

find_package(cryptominisat5 CONFIG REQUIRED)
find_package(arjun          CONFIG REQUIRED)
find_package(ganak          CONFIG REQUIRED)
find_package(sbva           CONFIG REQUIRED)
find_package(breakid        CONFIG REQUIRED)
find_package(approxmc       CONFIG REQUIRED)
find_package(klay           CONFIG REQUIRED)

find_library(CADICAL_LIB
  PATHS ${CMAKE_CURRENT_SOURCE_DIR}/../cadical/build/
  NAMES cadical
  REQUIRED)

find_library(CADIBACK_LIB
  PATHS ${CMAKE_CURRENT_SOURCE_DIR}/../cadiback/
  NAMES cadiback
  REQUIRED)

# -----------------------------------------------
# LIBRARY KOMPYLE
# -----------------------------------------------

add_library(kompyle SHARED
  src/core.cpp
)

target_include_directories(kompyle
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
        ${CRYPTOMINISAT5_INCLUDE_DIRS}
        ${KLAY_INCLUDE_DIRS}
        ${GANAK_INCLUDE_DIRS}
        ${ARJUN_INCLUDE_DIRS}
)

target_link_libraries(kompyle
    PUBLIC
        klay
        cryptominisat5
        arjun
        ganak
        sbva
        breakid
        approxmc
        ${CADICAL_LIB}
        ${CADIBACK_LIB}
)

# NOTE(Ibrahim):
# not needed if these dependencies are installed system-wide
# it needlessly increases the size of the wheel.
# https://github.com/scikit-build/scikit-build-core/issues/374
foreach(lib cryptominisat5 arjun ganak sbva breakid approxmc)
    get_target_property(lib_loc ${lib} LOCATION)
    install(FILES ${lib_loc} DESTINATION ${SKBUILD_PLATLIB_DIR}/kompyle)
endforeach()
# install(FILES ${CADICAL_LIB} ${CADIBACK_LIB} DESTINATION kompyle)


set(RPATH_ORIGIN "$ORIGIN")
if(APPLE)
  set(RPATH_ORIGIN "@loader_path")
endif()

set_target_properties(kompyle PROPERTIES
    INSTALL_RPATH "${RPATH_ORIGIN}:${RPATH_ORIGIN}/../klay"
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
    INSTALL_RPATH "${RPATH_ORIGIN}:${RPATH_ORIGIN}/../klay"
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
