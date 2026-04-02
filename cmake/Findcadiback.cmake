find_library(CADIBACK_LIB
  PATHS ${CMAKE_CURRENT_SOURCE_DIR}/../cadiback/
  NAMES cadiback
  REQUIRED)

if(NOT TARGET cadiback::cadiback)
    add_library(cadiback::cadiback STATIC IMPORTED)
    set_target_properties(cadiback::cadiback PROPERTIES
        IMPORTED_LOCATION ${CADIBACK_LIB})
endif()
