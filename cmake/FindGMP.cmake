find_path(GMP_INCLUDE_DIR NAMES gmp.h)
find_library(GMP_LIBRARY NAMES gmp)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(GMP
    REQUIRED_VARS
    GMP_INCLUDE_DIR
    GMP_LIBRARY
)

if(GMP_FOUND AND NOT TARGET GMP::gmp)
    add_library(GMP::gmp STATIC IMPORTED)
    set_target_properties(GMP::gmp PROPERTIES
        IMPORTED_LOCATION "${GMP_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${GMP_INCLUDE_DIR}"
    )
endif()
