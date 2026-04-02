find_library(CADICAL_LIB
  PATHS ${CMAKE_CURRENT_SOURCE_DIR}/../cadical/build/
  NAMES cadical
  REQUIRED)

if(NOT TARGET cadical::cadical)
    add_library(cadical::cadical STATIC IMPORTED)
    set_target_properties(cadical::cadical PROPERTIES
        IMPORTED_LOCATION ${CADICAL_LIB})
endif()
