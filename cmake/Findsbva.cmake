find_path(SBVA_INCLUDE_DIR
    NAMES sbva/sbva.h
    HINTS ${CMAKE_PREFIX_PATH}/include
)

find_library(SBVA_LIBRARY
    NAMES sbva
    HINTS ${CMAKE_PREFIX_PATH}/lib
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(sbva
    REQUIRED_VARS SBVA_LIBRARY SBVA_INCLUDE_DIR
)

# if(sbva_FOUND AND NOT TARGET sbva::sbva)
#   add_library(sbva::sbva SHARED IMPORTED)
#   set_target_properties(sbva::sbva PROPERTIES
#       IMPORTED_LOCATION             "${SBVA_LIBRARY}"
#       INTERFACE_INCLUDE_DIRECTORIES "${SBVA_INCLUDE_DIR}"
#   )
# endif()
if(sbva_FOUND AND NOT TARGET sbva::sbva)
    get_filename_component(SBVA_LIB_DIR ${SBVA_LIBRARY} DIRECTORY)
    add_library(sbva::sbva SHARED IMPORTED)
    set_target_properties(sbva::sbva PROPERTIES
        IMPORTED_LOCATION             "${SBVA_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${SBVA_INCLUDE_DIR}"
        INTERFACE_LINK_DIRECTORIES    "${SBVA_LIB_DIR}"
    )
endif()
