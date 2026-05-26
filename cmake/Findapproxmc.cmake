find_path(APPROXMC_INCLUDE_DIR
    NAMES approxmc/approxmc.h
    PATHS ${CMAKE_PREFIX_PATH}
    PATH_SUFFIXES include
)

find_library(APPROXMC_LIBRARY
    NAMES approxmc
    PATHS ${CMAKE_PREFIX_PATH}
    PATH_SUFFIXES lib lib64
)

# if(NOT APPROXMC_INCLUDE_DIR)
#     find_path(APPROXMC_INCLUDE_DIR NAMES approxmc.h PATH_SUFFIXES include)
# endif()
# if(NOT APPROXMC_LIBRARY)
#     find_library(APPROXMC_LIBRARY NAMES approxmc PATH_SUFFIXES lib lib64)
# endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(approxmc
    REQUIRED_VARS APPROXMC_LIBRARY APPROXMC_INCLUDE_DIR
)

if(approxmc_FOUND AND NOT TARGET approxmc::approxmc)
    add_library(approxmc::approxmc UNKNOWN IMPORTED)
    set_target_properties(approxmc::approxmc PROPERTIES
        IMPORTED_LOCATION             "${APPROXMC_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${APPROXMC_INCLUDE_DIR}"
    )
endif()
