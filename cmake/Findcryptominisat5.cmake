find_package(cryptominisat5 CONFIG QUIET)

set_target_properties(cryptominisat5 PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${CRYPTOMINISAT5_INCLUDE_DIRS}")
