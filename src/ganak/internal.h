// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Internal helpers shared between ganak compile and ganak count.

#ifndef SRC_GANAK_INTERNAL_H_
#define SRC_GANAK_INTERNAL_H_

#include <cstring>
#include <memory>
#include <string>
#include <vector>

#include "arjun/arjun.h"
#include "cryptominisat5/dimacsparser.h"
#include "cryptominisat5/solvertypesmini.h"
#include "ganak/ganak.hpp"

#include "ganak/arjun_options.h"
#include "kompyle/options.h"

namespace kmpyl {
namespace ganak_internal {

GanakInt::CounterConfiguration MakeGanakConf(const GanakOptions& opts);

void ReadDimacsInputFile(const std::string& cnf_file,
                         ArjunNS::SimplifiedCNF* cnf,
                         std::unique_ptr<CMSat::FieldGen>* fg);

void ConfigureArjun(ArjunNS::SimplifiedCNF* cnf,
                    ArjunNS::Arjun::ElimToFileConf& etof_conf);

void ConfigureArjunForCounting(
    ArjunNS::SimplifiedCNF* cnf,
    ArjunNS::Arjun::ElimToFileConf& etof_conf);

void RunArjun(ArjunNS::SimplifiedCNF* cnf, const ArjunConf& ac);

std::vector<GanakInt::Lit> CmsToGanakCl(const std::vector<CMSat::Lit>& cl);

std::vector<GanakInt::Lit> ArjunToGanakCl(
    const std::vector<CMSat::Lit>& cl,
    const std::vector<uint32_t>& var_to_ganak);

}  // namespace ganak_internal
}  // namespace kmpyl

#endif  // SRC_GANAK_INTERNAL_H_
