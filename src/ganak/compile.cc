// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/compile.h"

#include <cstdio>
#include <memory>
#include <set>
#include <string>
#include <vector>

#include "klay/node.h"
#include "ganak/ganak.hpp"
#include "cryptominisat5/dimacsparser.h"
#include "cryptominisat5/solvertypesmini.h"

#include "kompyle/kcircuit.h"
#include "kompyle/options.h"
#include "ganak/arjun_options.h"
#include "ganak/circuit_field.h"

namespace kmpyl {
namespace {

// ---------------------------------------------------------------------------
// Clause translation helpers
// ---------------------------------------------------------------------------

// Translate a CMSat clause into a Ganak clause, remapping var indices via
// `var_to_ganak`.
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

// Straight translation of a CMSat clause to Ganak, with 1-based re-indexing.
// See ganak/main.cpp or ganak/example.cpp in the Ganak source.
std::vector<GanakInt::Lit> CmsToGanakCl(const std::vector<CMSat::Lit>& cl) {
  std::vector<GanakInt::Lit> ganak_cl;
  ganak_cl.reserve(cl.size());
  for (const auto& l : cl) {
    ganak_cl.push_back(GanakInt::Lit(l.var() + 1, !l.sign()));
  }
  return ganak_cl;
}

// ---------------------------------------------------------------------------
// I/O helpers
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
// Arjun helpers
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

void RunArjun(ArjunNS::SimplifiedCNF* cnf, const ArjunConf& ac) {
  ArjunNS::Arjun arjun;
  arjun.set_verb(ac.arjun_verb);

  arjun.standalone_minimize_indep(*cnf, ac.etof_conf.all_indep);
  if (cnf->get_sampl_vars().size() >= ac.arjun_further_min_cutoff &&
      ac.do_puura) {
    arjun.standalone_elim_to_file(*cnf, ac.etof_conf, ac.simp_conf);
  }
}

// ---------------------------------------------------------------------------
// Ganak configuration helper
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

}  // namespace

// ---------------------------------------------------------------------------
// CompileFromCnfUsingGanak
// ---------------------------------------------------------------------------

klay::Node* CompileFromCnfUsingGanak(
    Circuit* circuit,
    const std::string& cnf_file,
    const GanakOptions& ganak_opts,
    const std::optional<ArjunOptions>& arjun_opts) {
  if (arjun_opts.has_value()) {
    // -----------------------------------------------------------------------
    // Arjun independent-support minimisation pre-pass, then Ganak.
    // -----------------------------------------------------------------------
    ArjunConf ac = MakeArjunConf(*arjun_opts);

    std::unique_ptr<CMSat::FieldGen> fg =
        std::make_unique<FGenCircuit>(circuit);
    ArjunNS::SimplifiedCNF cnf(fg);

    ReadDimacsInputFile(cnf_file, &cnf, &fg);
    ConfigureArjun(&cnf, ac.etof_conf);
    RunArjun(&cnf, ac);

    auto& mw = cnf.multiplier_weight;
    klay::Node* mw_node = dynamic_cast<FCircuit*>(mw.get())->get_node();

    // Fast-lookup set over the sampling variables still present after Arjun.
    const std::set<uint32_t> remaining_sampl_set(
        cnf.sampl_vars.begin(), cnf.sampl_vars.end());

    // Arjun adds and removes clauses; rebuild the active-variable set.
    std::set<uint32_t> all_active;
    for (const auto& cl : cnf.clauses)
      for (const auto& l : cl) all_active.insert(l.var());
    for (const auto& cl : cnf.red_clauses)
      for (const auto& l : cl) all_active.insert(l.var());

    const auto& cweights = cnf.weights;

    // Build Arjun-var -> Ganak-var remap.  Ganak expects independents first.
    std::vector<uint32_t> var_to_ganak(cnf.nVars(), 0);
    uint32_t next_gv = 1;
    for (uint32_t v : cnf.sampl_vars) {
      if (all_active.count(v)) var_to_ganak[v] = next_gv++;
    }
    const uint32_t indep_end = next_gv;

    for (uint32_t v : all_active) {
      if (!remaining_sampl_set.count(v) && cweights.count(v)) {
        var_to_ganak[v] = next_gv++;
      }
    }
    const uint32_t opt_indep_end = next_gv;

    for (uint32_t v : all_active) {
      if (var_to_ganak[v] == 0) var_to_ganak[v] = next_gv++;
    }
    const uint32_t total_gv = next_gv - 1;

    std::unique_ptr<CMSat::FieldGen> ganak_fg = cnf.fg->dup();
    GanakInt::CounterConfiguration gconf = MakeGanakConf(ganak_opts);

    Ganak counter(gconf, ganak_fg);

    if (total_gv == 0) {
      counter.new_vars(cnf.nVars());
      counter.set_indep_support({});
      counter.set_optional_indep_support({});
      for (const auto& cl : cnf.clauses)
        counter.add_irred_cl(CmsToGanakCl(cl));
      for (const auto& cl : cnf.red_clauses)
        counter.add_red_cl(CmsToGanakCl(cl));
    } else {
      counter.new_vars(total_gv);

      std::set<uint32_t> indeps;
      std::set<uint32_t> opt_indeps;
      for (uint32_t i = 1; i < indep_end;     ++i) indeps.insert(i);
      for (uint32_t i = 1; i < opt_indep_end; ++i) opt_indeps.insert(i);

      counter.set_indep_support(indeps);
      counter.set_optional_indep_support(opt_indeps);

      for (const auto& cl : cnf.clauses)
        counter.add_irred_cl(ArjunToGanakCl(cl, var_to_ganak));
      for (const auto& cl : cnf.red_clauses)
        counter.add_red_cl(ArjunToGanakCl(cl, var_to_ganak));

      for (uint32_t v : all_active) {
        const uint32_t gv = var_to_ganak[v];
        if (gv >= opt_indep_end) continue;
        counter.set_lit_weight(GanakInt::Lit(gv, true),
                               cweights.at(v).pos->dup());
        counter.set_lit_weight(GanakInt::Lit(gv, false),
                               cweights.at(v).neg->dup());
      }
    }

    auto result = counter.count();
    klay::Node* g_node = dynamic_cast<FCircuit*>(result.get())->get_node();

    if (g_node->is_false()) return circuit->false_node().get();
    if (mw_node->is_true())  return g_node;
    if (g_node->is_true())   return mw_node;
    return circuit->and_node({klay::NodePtr(mw_node), klay::NodePtr(g_node)})
        .get();
  }

  // -------------------------------------------------------------------------
  // No Arjun pre-pass: feed the CNF directly to Ganak.
  // -------------------------------------------------------------------------
  std::unique_ptr<CMSat::FieldGen> fg =
      std::make_unique<FGenCircuit>(circuit);

  ArjunNS::SimplifiedCNF cnf(fg);
  ReadDimacsInputFile(cnf_file, &cnf, &fg);

  if (!cnf.get_sampl_vars_set()) {
    std::vector<uint32_t> all;
    all.reserve(cnf.nVars());
    for (uint32_t i = 0; i < cnf.nVars(); ++i) all.push_back(i);
    cnf.set_sampl_vars(all);
  }

  std::set<uint32_t> indeps;
  std::set<uint32_t> opt_indeps;
  for (uint32_t v : cnf.sampl_vars)     indeps.insert(v + 1);
  for (uint32_t v : cnf.opt_sampl_vars) opt_indeps.insert(v + 1);
  if (opt_indeps.empty()) opt_indeps = indeps;

  GanakInt::CounterConfiguration conf = MakeGanakConf(ganak_opts);

  Ganak counter(conf, fg);
  counter.new_vars(cnf.nVars());
  counter.set_indep_support(indeps);
  counter.set_optional_indep_support(opt_indeps);

  for (const auto& cl : cnf.clauses)     counter.add_irred_cl(CmsToGanakCl(cl));
  for (const auto& cl : cnf.red_clauses) counter.add_red_cl(CmsToGanakCl(cl));

  auto* fg_r = dynamic_cast<FGenCircuit*>(fg.get());
  for (uint32_t v : indeps) {
    counter.set_lit_weight(GanakInt::Lit(v, true),
                           fg_r->lit_field(+static_cast<int>(v)));
    counter.set_lit_weight(GanakInt::Lit(v, false),
                           fg_r->lit_field(-static_cast<int>(v)));
  }

  auto result = counter.count();
  auto* fc = dynamic_cast<FCircuit*>(result.get());
  return fc->get_node();
}

}  // namespace kmpyl
