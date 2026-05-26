// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "ganak/internal.h"

#include <cerrno>
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "ganak/circuit_field.h"
#include "ganak/count_field.h"

namespace kmpyl {
namespace ganak_internal {

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

GanakInt::CounterConfiguration MakeGanakConf(const GanakOptions& opts) {
  GanakInt::CounterConfiguration conf;

  // Basic
  conf.verb                  = opts.verb;
  conf.do_chronobt           = opts.do_chronobt         ? 1 : 0;
  conf.do_use_sat_solver     = opts.do_use_sat_solver   ? 1 : 0;

  // Restarts
  conf.do_restart            = opts.do_restart          ? 1 : 0;
  if (opts.first_restart.has_value()) {
    conf.first_restart = *opts.first_restart;
  }

  // Cache
  conf.maximum_cache_size_MB = opts.maximum_cache_size_mb;

  // Branching polarity
  conf.polar_type            = static_cast<int>(opts.polar_type);

  // Clause DB reduction
  conf.rdb_keep_used         = opts.rdb_keep_used       ? 1 : 0;

  // Tree decomposition
  conf.do_td                 = opts.do_td               ? 1 : 0;
  conf.td_varlim             = opts.td_var_limit;
  conf.td_maxweight          = opts.td_max_weight;
  conf.td_minweight          = opts.td_min_weight;
  conf.td_divider            = opts.td_divider;
  conf.td_exp_mult           = opts.td_exp_mult;
  conf.td_iters              = opts.td_iters;

  return conf;
}

// ---------------------------------------------------------------------------
// CNF loading
// ---------------------------------------------------------------------------

void ReadDimacsInputFile(const std::string& cnf_file,
                         ArjunNS::SimplifiedCNF* cnf,
                         std::unique_ptr<CMSat::FieldGen>* fg) {
  FILE* in = std::fopen(cnf_file.c_str(), "rb");
  if (in == nullptr) {
    throw std::runtime_error(
        "cannot open '" + cnf_file + "': " + std::strerror(errno));
  }

  CMSat::DimacsParser<
      CMSat::StreamBuffer<FILE*, CMSat::FN>,
      ArjunNS::SimplifiedCNF>
      parser(cnf, nullptr, 0, *fg);

  if (!parser.parse_DIMACS(in, true)) {
    std::fclose(in);
    throw std::runtime_error("DIMACS parse error in '" + cnf_file + "'");
  }
  std::fclose(in);
}

// ---------------------------------------------------------------------------
// Arjun (compile path — needs per-literal FCircuit weights)
// ---------------------------------------------------------------------------

void ConfigureArjun(ArjunNS::SimplifiedCNF* cnf,
                    ArjunNS::Arjun::ElimToFileConf& etof_conf) {
  auto* fg_r = dynamic_cast<FGenCircuit*>(cnf->fg.get());
  assert(fg_r && "cnf->fg must be an FGenCircuit");

  if (!cnf->get_sampl_vars_set()) {
    etof_conf.all_indep = true;
    std::vector<uint32_t> sampl_vars;
    sampl_vars.reserve(cnf->nVars());
    for (uint32_t i = 0; i < cnf->nVars(); ++i) sampl_vars.push_back(i);
    cnf->set_sampl_vars(sampl_vars);
  }

  cnf->set_weighted(true);
  for (uint32_t v : cnf->sampl_vars) {
    cnf->set_lit_weight(CMSat::Lit(v, false),
                        fg_r->lit_field(+static_cast<int>(v + 1)));
    cnf->set_lit_weight(CMSat::Lit(v, true),
                        fg_r->lit_field(-static_cast<int>(v + 1)));
  }
  cnf->check_sanity();
}


// ---------------------------------------------------------------------------
// Arjun (count path — no FCircuit weighting needed)
// ---------------------------------------------------------------------------

void ConfigureArjunForCounting(
    ArjunNS::SimplifiedCNF* cnf,
    ArjunNS::Arjun::ElimToFileConf& etof_conf) {
  if (!cnf->get_sampl_vars_set()) {
    etof_conf.all_indep = true;
    std::vector<uint32_t> sampl_vars;
    sampl_vars.reserve(cnf->nVars());
    for (uint32_t i = 0; i < cnf->nVars(); ++i) sampl_vars.push_back(i);
    cnf->set_sampl_vars(sampl_vars);
  }

  if (cnf->fg->weighted()) {
    auto* fg_r = dynamic_cast<FGenCount*>(cnf->fg.get());
    cnf->set_weighted(true);
    for (uint32_t v : cnf->sampl_vars) {
      cnf->set_lit_weight(CMSat::Lit(v, false), fg_r->one());
      cnf->set_lit_weight(CMSat::Lit(v, true),  fg_r->one());
    }
    cnf->check_sanity();
  }
}

void RunArjun(ArjunNS::SimplifiedCNF* cnf, const ArjunConf& ac) {
  ArjunNS::Arjun arjun;
  arjun.set_verb(ac.arjun_verb);
  arjun.set_probe_based(ac.do_probe_based);
  arjun.set_simp(ac.arjun_simp_level);
  arjun.set_backw_max_confl(ac.arjun_backw_maxc);
  arjun.set_oracle_find_bins(ac.arjun_oracle_find_bins);
  arjun.set_cms_glob_mult(ac.arjun_cms_glob_mult);
  arjun.set_extend_max_confl(ac.arjun_extend_max_confl);
  arjun.set_extend_ccnr(ac.arjun_extend_ccnr);
  arjun.set_autarkies(ac.arjun_autarkies);

  // arjun.standalone_minimize_indep(*cnf, ac.etof_conf.all_indep);
  if (cnf->get_sampl_vars().size() >= ac.arjun_further_min_cutoff && ac.do_puura) {
    arjun.standalone_elim_to_file(*cnf, ac.etof_conf, ac.simp_conf);
  }
}

// ---------------------------------------------------------------------------
// Clause translation
// ---------------------------------------------------------------------------

std::vector<GanakInt::Lit> CmsToGanakCl(const std::vector<CMSat::Lit>& cl) {
  std::vector<GanakInt::Lit> ganak_cl;
  ganak_cl.reserve(cl.size());
  for (const auto& l : cl) {
    ganak_cl.push_back(GanakInt::Lit(l.var() + 1, !l.sign()));
  }
  return ganak_cl;
}

std::vector<GanakInt::Lit> ArjunToGanakCl(
    const std::vector<CMSat::Lit>& cl,
    const std::vector<uint32_t>& var_to_ganak) {
  std::vector<GanakInt::Lit> out;
  out.reserve(cl.size());
  for (const auto& l : cl) {
    const uint32_t gv = var_to_ganak[l.var()];
    assert(gv != 0 && "clause variable missing from remap table");
    out.push_back(GanakInt::Lit(gv, !l.sign()));
  }
  return out;
}

}  // namespace ganak_internal
}  // namespace kmpyl
