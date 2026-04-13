find_library(D4_LIB
  PATHS ${CMAKE_CURRENT_SOURCE_DIR}/../d4v2/build
  NAMES d4
  REQUIRED)

if(NOT TARGET d4::d4)
    add_library(d4::d4 STATIC IMPORTED)
    set_target_properties(d4::d4 PROPERTIES
        IMPORTED_LOCATION ${D4_LIB}
        INTERFACE_INCLUDE_DIRECTORIES ${CMAKE_CURRENT_SOURCE_DIR}/../d4v2)
endif()
