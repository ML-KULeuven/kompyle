find_library(MD4_LIBRARY
    NAMES md4
    PATHS ${CMAKE_PREFIX_PATH}
    PATH_SUFFIXES lib lib64
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(md4
    REQUIRED_VARS MD4_LIBRARY # MD4_INCLUDE_DIR
)

if(md4_FOUND AND NOT TARGET md4::d4)
    add_library(md4::d4 UNKNOWN IMPORTED)
    set_target_properties(md4::d4 PROPERTIES
        IMPORTED_LOCATION             "${MD4_LIBRARY}"
        # INTERFACE_INCLUDE_DIRECTORIES "${MD4_INCLUDE_DIR}"
    )
endif()
