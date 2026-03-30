// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#pragma once

#include <cryptominisat5/solvertypesmini.h>
#include <cryptominisat5/dimacsparser.h>
#include <ganak/ganak.hpp>
#include <ganak/lit.hpp>
#include <arjun/arjun.h>
#include <klay/circuit.h>
#include <klay/node.h>

#include "field_circuit.h"
#include "constants.h"

Node* compile_from_ganak(
    Circuit* circ,
    const std::string& cnf_file);

Node* compile_from_ganak_with_arjun(
    Circuit* circ,
    const std::string& cnf_file);
