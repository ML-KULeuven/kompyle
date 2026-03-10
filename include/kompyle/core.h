// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#pragma once

#include "field_circuit.h"

#include <cryptominisat5/solvertypesmini.h>
#include <cryptominisat5/dimacsparser.h>
#include <ganak/ganak.hpp>
#include <ganak/lit.hpp>
#include <arjun/arjun.h>
#include <klay/circuit.h>

#include <memory>
#include <vector>

NodePtr
compile_from_ganak(
    const std::string& cnf_file);

NodePtr
compile_from_ganak(
    Circuit* circ,
    const std::string& cnf_file);
