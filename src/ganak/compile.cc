// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/compile.h"

#include <boost/multiprecision/fwd.hpp>
#include <cstdio>
#include <memory>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include <boost/multiprecision/gmp.hpp>
#include <klay/node.h>
#include <ganak/ganak.hpp>
#include <cryptominisat5/dimacsparser.h>
#include <cryptominisat5/solvertypesmini.h>
#include <arjun/arjun.h>

#include "ganak/field_stats.h"
#include "kompyle/kcircuit.h"
#include "kompyle/options.h"
#include "ganak/arjun_options.h"
#include "ganak/count_field.h"
#include "ganak/circuit_field.h"
#include "ganak/internal.h"

namespace kmpyl {
namespace {

using ganak_internal::ArjunToGanakCl;
using ganak_internal::CmsToGanakCl;
using ganak_internal::ConfigureArjun;
using ganak_internal::ConfigureArjunForCounting;
using ganak_internal::MakeGanakConf;
using ganak_internal::ReadDimacsInputFile;
using ganak_internal::RunArjun;

boost::multiprecision::mpz_int ExtractMpz(const CMSat::Field* f) {
  if (f == nullptr) return 0;
  const auto* fm = dynamic_cast<const FCount*>(f);
  return fm ? fm->val : boost::multiprecision::mpz_int(0);
}

}  // namespace

// ---------------------------------------------------------------------------
// CompileFromCnfUsingGanak
// ---------------------------------------------------------------------------

klay::Node* CompileFromCnfUsingGanak(
    Circuit* circuit,
    const std::string& cnf_file,
    const GanakOptions& ganak_opts,
    const ArjunOptions& arjun_opts) {
  if (arjun_opts.do_arjun) {
    // -----------------------------------------------------------------------
    // Arjun independent-support minimisation pre-pass, then Ganak.
    // -----------------------------------------------------------------------
    ArjunConf ac = MakeArjunConf(arjun_opts);

    std::unique_ptr<CMSat::FieldGen> fg =
        std::make_unique<FGenCircuit>(circuit);
    ArjunNS::SimplifiedCNF cnf(fg);

    ReadDimacsInputFile(cnf_file, &cnf, &fg);
    ConfigureArjun(&cnf, ac.etof_conf);
    RunArjun(&cnf, ac);

    auto& mw = cnf.multiplier_weight;
    klay::Node* mw_node = dynamic_cast<FCircuit*>(mw.get())->get_node();

    const std::set<uint32_t> remaining_sampl_set(
        cnf.sampl_vars.begin(), cnf.sampl_vars.end());

    std::set<uint32_t> all_active;
    for (const auto& cl : cnf.clauses)
      for (const auto& l : cl) all_active.insert(l.var());
    for (const auto& cl : cnf.red_clauses)
      for (const auto& l : cl) all_active.insert(l.var());

    const auto& cweights = cnf.weights;

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
        if (gv >= opt_indep_end || !cweights.count(v)) continue;
        counter.set_lit_weight(GanakInt::Lit(gv, true),
                               cweights.at(v).pos->dup());
        counter.set_lit_weight(GanakInt::Lit(gv, false),
                               cweights.at(v).neg->dup());
      }
    }

    auto result = counter.count();
    klay::Node* g_node = dynamic_cast<FCircuit*>(result.get())->get_node();

    // g_gk_stats_circuit.print();
    if (g_node->is_false())   return circuit->false_node().get();
    if (mw_node->is_true())   return g_node;
    if (g_node->is_true())    return mw_node;
    return circuit->and_node({klay::NodePtr(mw_node), klay::NodePtr(g_node)}).get();
    // return circuit->false_node().get();
  }

  // -------------------------------------------------------------------------
  // No Arjun pre-pass: feed the CNF directly to Ganak.
  // -------------------------------------------------------------------------
  std::unique_ptr<CMSat::FieldGen> fg =
      std::make_unique<FGenCircuit>(circuit);
  // std::unique_ptr<CMSat::FieldGen> fg =
  //     std::make_unique<CMSat::FGenDouble>();

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
    // counter.set_lit_weight(GanakInt::Lit(v, false), fg->one());
    // counter.set_lit_weight(GanakInt::Lit(v, true), fg->one());
    counter.set_lit_weight(GanakInt::Lit(v, true),
                           fg_r->lit_field(+static_cast<int>(v)));
    counter.set_lit_weight(GanakInt::Lit(v, false),
                           fg_r->lit_field(-static_cast<int>(v)));
  }

  auto result = counter.count();
  auto* fc = dynamic_cast<FCircuit*>(result.get());

  // g_gk_stats_circuit.print();
  return fc->get_node();
  // return circuit->false_node().get();
}


// ---------------------------------------------------------------------------
// CountFromCnfUsingGanak
// ---------------------------------------------------------------------------

boost::multiprecision::mpz_int CountFromCnfUsingGanak(
    const std::string& cnf_file,
    const GanakOptions& ganak_opts,
    const ArjunOptions& arjun_opts,
    bool weighted_counting) {
  using mpz_int = boost::multiprecision::mpz_int;

  // auto extract_mpz = [](const CMSat::Field& f) -> mpz::mpz_int {
  //   const ArjunNS::FMpz& fm = dynamic_cast<const ArjunNS::FMpz&>(f);
  //   return mpz::mpz_int(fm.val.get_mpz_t());
  // };

  if (arjun_opts.do_arjun) {
    ArjunConf ac = MakeArjunConf(arjun_opts);

    // std::unique_ptr<CMSat::FieldGen> fg = std::make_unique<ArjunNS::FGenMpz>();
    std::unique_ptr<CMSat::FieldGen> fg =
      std::make_unique<FGenCount>(weighted_counting);

    ArjunNS::SimplifiedCNF cnf(fg);

    ReadDimacsInputFile(cnf_file, &cnf, &fg);
    ConfigureArjunForCounting(&cnf, ac.etof_conf);
    RunArjun(&cnf, ac);
    // cnf.write_simpcnf("/tmp/after_puura.cnf");
    // cnf.write_simpcnf("/tmp/after_puura_unred.cnf", false);


    auto& mw = cnf.multiplier_weight;
    // klay::Node* mw_node = dynamic_cast<FCircuit*>(mw.get())->get_node();

    const std::set<uint32_t> remaining_sampl_set(
        cnf.sampl_vars.begin(), cnf.sampl_vars.end());

    std::set<uint32_t> all_active;
    for (const auto& cl : cnf.clauses)
      for (const auto& l : cl) all_active.insert(l.var());
    for (const auto& cl : cnf.red_clauses)
      for (const auto& l : cl) all_active.insert(l.var());

    const auto& cweights = cnf.weights;

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
      for (uint32_t i = 1; i < indep_end; ++i) indeps.insert(i);
      for (uint32_t i = 1; i < opt_indep_end; ++i) opt_indeps.insert(i);

      counter.set_indep_support(indeps);
      counter.set_optional_indep_support(opt_indeps);

      for (const auto& cl : cnf.clauses)
        counter.add_irred_cl(ArjunToGanakCl(cl, var_to_ganak));
      for (const auto& cl : cnf.red_clauses)
        counter.add_red_cl(ArjunToGanakCl(cl, var_to_ganak));

      for (uint32_t v : all_active) {
        const uint32_t gv = var_to_ganak[v];
        if (gv >= opt_indep_end || !cweights.count(v)) continue;
        counter.set_lit_weight(GanakInt::Lit(gv, true),
                               cweights.at(v).pos->dup());
        counter.set_lit_weight(GanakInt::Lit(gv, false),
                               cweights.at(v).neg->dup());
      }
    }

    // std::cerr << "[kompyle] post-PUURA:"
    //       << " nVars=" << cnf.nVars()
    //       << " clauses=" << cnf.clauses.size()
    //       << " red_clauses=" << cnf.red_clauses.size()
    //       << " sampl=" << cnf.sampl_vars.size()
    //       << " opt_sampl=" << cnf.opt_sampl_vars.size()
    //       << " weights=" << cnf.weights.size()
    //       << " mw_is_one=" << cnf.multiplier_weight->is_one()
    //       << " mw_is_zero=" << cnf.multiplier_weight->is_zero()
    //       << " total_gv=" << total_gv
    //       << " indep_end=" << indep_end
    //       << std::endl;
    // std::cerr.flush();

    auto result = counter.count();

    // auto cnt = cnf.multiplier_weight->dup();
    // if (!cnf.multiplier_weight->is_zero()) *cnt *= *result;

    mpz_int mult = ExtractMpz(cnf.multiplier_weight.get());
    mpz_int sub  = ExtractMpz(result.get());
    mpz_int cnt  = cnf.multiplier_weight->is_zero() ? mpz_int(0) : mult * sub;

    // g_gk_stats_count.print();
    return cnt;
  }

  std::unique_ptr<CMSat::FieldGen> fg =
      std::make_unique<FGenCount>(weighted_counting);

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

  if (weighted_counting) {
    for (uint32_t v : indeps) {
      counter.set_lit_weight(GanakInt::Lit(v, true),  fg->one());
      counter.set_lit_weight(GanakInt::Lit(v, false), fg->one());
    }
  }

  auto result = counter.count();
  mpz_int cnt = ExtractMpz(result.get());

  // g_gk_stats_count.print();
  // auto& fm = dynamic_cast<const FDoubleInstrumented&>(result);
  // result.get();
  return cnt;
}

}  // namespace kmpyl
