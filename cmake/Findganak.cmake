find_package(ganak CONFIG REQUIRED)

set_target_properties(ganak PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${GANAK_INCLUDE_DIRS}")
