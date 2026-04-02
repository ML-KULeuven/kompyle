find_package(arjun CONFIG REQUIRED)

set_target_properties(arjun PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${ARJUN_INCLUDE_DIRS}")
