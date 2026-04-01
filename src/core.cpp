// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/core.h"
#include "kompyle/constants.h"


vector<GanakInt::Lit>
arjun_to_ganak_cl(const vector<CMSat::Lit>& cl,
             const vector<uint32_t>& var_to_ganak)
{
  vector<GanakInt::Lit> out;
  out.reserve(cl.size());
  for (const auto& l : cl) {
    const uint32_t gv = var_to_ganak[l.var()];
    assert(gv != 0 && "clause variable missing from remap table");
    out.push_back(GanakInt::Lit(gv, !l.sign()));
  }
  return out;
}


void 
read_dimacs_input_file(
    const std::string& cnf_file,
    ArjunNS::SimplifiedCNF& cnf,
    std::unique_ptr<CMSat::FieldGen>& fg) {
  FILE * in;
  in = std::fopen(cnf_file.c_str(), "rb");

  if (in == nullptr) {
    throw std::runtime_error("cannot open '"
      + cnf_file + "': " + std::strerror(errno));
  }

  CMSat::DimacsParser<
    CMSat::StreamBuffer<FILE*, CMSat::FN>,
    ArjunNS::SimplifiedCNF> parser(&cnf, nullptr, 0, fg);

  if (!parser.parse_DIMACS(in, true)) {
    std::fclose(in);
    throw std::runtime_error("DIMACS parse error in '"
      + cnf_file + "'");
  }
  std::fclose(in);
}


void
confure_arjun(ArjunNS::SimplifiedCNF& cnf,
  ArjunNS::Arjun::ElimToFileConf etof_conf,
  ArjunNS::SimpConf simp_conf) {

  auto* fg_r = dynamic_cast<FGenCircuit*>(cnf.fg.get());
  assert(fg_r && "cnf.fg must be an FGenCircuit");

  if (!cnf.get_sampl_vars_set()) {
    etof_conf.all_indep = true;
    std::vector<uint32_t> smpld_vars;
    smpld_vars.reserve(cnf.nVars());
    for (uint32_t i = 0; i < cnf.nVars(); ++i) smpld_vars.push_back(i);
    cnf.set_sampl_vars(smpld_vars); 
  }

  // if (cnf.get_weighted()) {
  //   throw std::runtime_error(
  //       "This library constructs circuits from cnf files, "
  //       "provide unweighted cnf files.");
  // }

  cnf.set_weighted(true);
  for (uint32_t v : cnf.sampl_vars) {
    cnf.set_lit_weight(CMSat::Lit(v, false),
                       fg_r->lit_field(+(int)(v + 1)));
    cnf.set_lit_weight(CMSat::Lit(v, true),
                       fg_r->lit_field(-(int)(v + 1)));
  }
  cnf.check_sanity();
}


void
run_arjun(ArjunNS::SimplifiedCNF& cnf,
          ArjunOptions& ao) {
  ArjunNS::Arjun arjun;
  // arjun.set_verb(ao.arjun_verb);
  // arjun.set_or_gate_based(ao.arjun_gates);
  // arjun.set_xor_gates_based(ao.arjun_gates);
  // arjun.set_ite_gate_based(ao.arjun_gates);
  // arjun.set_irreg_gate_based(ao.arjun_gates);
  // arjun.set_extend_max_confl(ao.arjun_extend_max_confl);
  // arjun.set_probe_based(ao.do_probe_based);
  // arjun.set_simp(ao.arjun_simp_level);
  // arjun.set_backw_max_confl(ao.arjun_backw_maxc);
  // arjun.set_oracle_find_bins(ao.arjun_oracle_find_bins);
  // arjun.set_cms_glob_mult(ao.arjun_cms_glob_mult);
  // arjun.set_autarkies(ao.arjun_autarkies);
  // if (ao.do_pre_backbone) arjun.standalone_backbone(cnf);

  arjun.standalone_minimize_indep(cnf, ao.etof_conf.all_indep);
  // arjun.set_extend_ccnr(ao.arjun_extend_ccnr);
  if (cnf.get_sampl_vars().size() >= ao.arjun_further_min_cutoff && ao.do_puura) {
    arjun.standalone_elim_to_file(cnf, ao.etof_conf, ao.simp_conf);
  }
}


// NOTE(Ibrahim):
// from ganak source code,
// see ganak/main.cpp or ganak/example.cpp
vector<GanakInt::Lit>
cms_to_ganak_cl(const vector<CMSat::Lit>& cl) {
  vector<GanakInt::Lit> ganak_cl;
  ganak_cl.reserve(cl.size());
  for(const auto& l: cl)
    ganak_cl.push_back(GanakInt::Lit(l.var()+1, !l.sign()));
  return ganak_cl;
}


Node*
compile_from_cnf_using_ganak(
    Circuit* circ,
    const std::string& cnf_file) {
  std::unique_ptr<CMSat::FieldGen> fg;
  fg = std::make_unique<FGenCircuit>(circ);

  ArjunNS::SimplifiedCNF cnf(fg);

  read_dimacs_input_file(cnf_file, cnf, fg);

  if (!cnf.get_sampl_vars_set()) {
    std::vector<uint32_t> all;
    all.reserve(cnf.nVars());
    for (uint32_t i = 0; i < cnf.nVars(); ++i) all.push_back(i);
    cnf.set_sampl_vars(all);
  }

  std::set<uint32_t> indeps, opt_indeps;
  for (uint32_t v : cnf.sampl_vars)     indeps.insert(v + 1);
  for (uint32_t v : cnf.opt_sampl_vars) opt_indeps.insert(v + 1);
  if (opt_indeps.empty()) opt_indeps = indeps;

  GanakInt::CounterConfiguration conf;
  conf.verb        = 0;

  Ganak counter(conf, fg);
  counter.new_vars(cnf.nVars());
  counter.set_indep_support(indeps);
  counter.set_optional_indep_support(opt_indeps);

  for (const auto& cl : cnf.clauses)     counter.add_irred_cl(cms_to_ganak_cl(cl));
  for (const auto& cl : cnf.red_clauses) counter.add_red_cl(cms_to_ganak_cl(cl));

  auto* fg_r = dynamic_cast<FGenCircuit*>(fg.get());
  for (uint32_t v : indeps) {
    counter.set_lit_weight(GanakInt::Lit(v, true),  fg_r->lit_field(+(int)v));
    counter.set_lit_weight(GanakInt::Lit(v, false), fg_r->lit_field(-(int)v));
  }

  auto result = counter.count();

  FCircuit* fc = dynamic_cast<FCircuit*>(result.get());
  return fc->get_node();

  // FIXME(Ibrahim):
  // * if restart -> rmeoved unused could be done.
  // * arjun is important
  // * make sure to use as much as possible of ganak
}


Node*
compile_from_cnf_using_ganakarjun(
    Circuit* circ,
    const std::string& cnf_file)
{
  ArjunOptions ao;
  std::unique_ptr<CMSat::FieldGen> fg;
  fg = std::make_unique<FGenCircuit>(circ);
  ArjunNS::SimplifiedCNF cnf(fg);

  read_dimacs_input_file(cnf_file, cnf, fg);
  confure_arjun(cnf, ao.etof_conf, ao.simp_conf);
  run_arjun(cnf, ao);

  auto& mw = cnf.multiplier_weight;
  Node* mw_node = dynamic_cast<FCircuit*>(mw.get())->get_node();

  // NOTE(Ibrahim):
  // fast lookup structures
  const std::set<uint32_t> remaining_sampl_set(
      cnf.sampl_vars.begin(), cnf.sampl_vars.end());
  std::set<uint32_t> all_active;

  // NOTE(Ibrahim):
  // arjun adds clauses, removes them, so find out
  // which variables are still active
  for (const auto& cl : cnf.clauses)
    for (const auto& l : cl) all_active.insert(l.var());
  for (const auto& cl : cnf.red_clauses)
    for (const auto& l : cl) all_active.insert(l.var());

  // NOTE(Ibrahim):
  // arjun adjusts weights of the literals,
  // see arjun fix_weights
  const auto& cweights = cnf.weights;

  std::vector<uint32_t> var_to_ganak(cnf.nVars(), 0);
  uint32_t next_gv = 1;

  // NOTE(Ibrahim):
  // see arjun `renumber_sampling_vars_for_ganak`
  // ganak expects variable numbering to start with indep
  for (uint32_t v : cnf.sampl_vars)
    if (all_active.count(v))
      var_to_ganak[v] = next_gv++;
  const uint32_t indep_end = next_gv;

  for (uint32_t v : all_active)
    // NOTE(Ibrahim):
    // use cweights and not opt_sampl_vars!
    if (!remaining_sampl_set.count(v) && cweights.count(v))
      var_to_ganak[v] = next_gv++;
  const uint32_t opt_indep_end = next_gv;

  for (uint32_t v : all_active)
    if (var_to_ganak[v] == 0)
      var_to_ganak[v] = next_gv++;
  const uint32_t total_gv = next_gv - 1;

  std::unique_ptr<CMSat::FieldGen> ganak_fg = cnf.fg->dup();
  GanakInt::CounterConfiguration gconf;
  gconf.verb        = 0;

  Ganak counter(gconf, ganak_fg);

  if (total_gv == 0) {
    counter.new_vars(cnf.nVars());
    counter.set_indep_support({});
    counter.set_optional_indep_support({});
    for (const auto& cl : cnf.clauses)
      counter.add_irred_cl(cms_to_ganak_cl(cl));
    for (const auto& cl : cnf.red_clauses)
      counter.add_red_cl(cms_to_ganak_cl(cl));

  } else {
    counter.new_vars(total_gv);

    std::set<uint32_t> indeps, opt_indeps;
    for (uint32_t i = 1; i < indep_end;     ++i) indeps.insert(i);
    for (uint32_t i = 1; i < opt_indep_end; ++i) opt_indeps.insert(i);

    counter.set_indep_support(indeps);
    counter.set_optional_indep_support(opt_indeps);

    for (const auto& cl : cnf.clauses)
      // NOTE(Ibrahim):
      // see arjun `renumber_sampling_vars_for_ganak`
      counter.add_irred_cl(arjun_to_ganak_cl(cl, var_to_ganak));
    for (const auto& cl : cnf.red_clauses)
      // NOTE(Ibrahim):
      // see arjun `renumber_sampling_vars_for_ganak`
      counter.add_red_cl(arjun_to_ganak_cl(cl, var_to_ganak));

    for (uint32_t v : all_active) {
      const uint32_t gv = var_to_ganak[v];
      if (gv >= opt_indep_end) continue;
      counter.set_lit_weight(GanakInt::Lit(gv, true),  cweights.at(v).pos->dup());
      counter.set_lit_weight(GanakInt::Lit(gv, false), cweights.at(v).neg->dup());
    }
  }

  auto result  = counter.count();
  Node* g_node = dynamic_cast<FCircuit*>(result.get())->get_node();

  if (g_node->is_false()) return circ->false_node().get();
  if (mw_node->is_true()) return g_node;
  if (g_node->is_true())  return mw_node;
  return circ->and_node({NodePtr(mw_node), NodePtr(g_node)}).get();
}
