// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#pragma once

#include <stdexcept>

#include <cryptominisat5/solvertypesmini.h>
#include <cryptominisat5/dimacsparser.h>
#include <ganak/ganak.hpp>
#include <ganak/lit.hpp>
#include <arjun/arjun.h>
#include <klay/circuit.h>
#include <klay/node.h>

extern "C" {
  #include <sdd/sddapi.h>
  #include <sdd/compiler.h>
}

#include "field_circuit.h"
#include "constants.h"

Node* compile_from_cnf_using_ganak(
    Circuit* circ,
    const std::string& cnf_file);

Node* compile_from_cnf_using_ganakarjun(
    Circuit* circ,
    const std::string& cnf_file);


Node* compile_from_cnf_using_sdd(
    Circuit* circ,
    const std::string& cnf_file);

Node* compile_from_sdd(
    Circuit* circ,
    SddNode* root);
