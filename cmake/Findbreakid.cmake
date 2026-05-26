find_path(BREAKID_INCLUDE_DIR
    NAMES breakid/breakid.hpp
    PATHS ${CMAKE_PREFIX_PATH}
    PATH_SUFFIXES include
)

find_library(BREAKID_LIBRARY
    NAMES breakid
    PATHS ${CMAKE_PREFIX_PATH}
    PATH_SUFFIXES lib lib64
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(breakid
    REQUIRED_VARS BREAKID_LIBRARY BREAKID_INCLUDE_DIR
)

if(breakid_FOUND AND NOT TARGET breakid::breakid)
    add_library(breakid::breakid UNKNOWN IMPORTED)
    set_target_properties(breakid::breakid PROPERTIES
        IMPORTED_LOCATION             "${BREAKID_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${BREAKID_INCLUDE_DIR}"
    )
endif()
