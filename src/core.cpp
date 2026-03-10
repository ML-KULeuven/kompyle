// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/core.h"

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

NodePtr
compile_from_ganak(const std::string& cnf_file) {
  auto circ = std::make_unique<Circuit>();
  return compile_from_ganak(circ.get(), cnf_file);
}

NodePtr
compile_from_ganak(
    Circuit* circ,
    const std::string& cnf_file) {
  std::unique_ptr<CMSat::FieldGen> fg;
  fg = std::make_unique<FGenCircuit>(circ);

  ArjunNS::SimplifiedCNF cnf(fg);

  FILE* in = std::fopen(cnf_file.c_str(), "rb");
  if (!in)
    throw std::runtime_error("compile_to_ganak_into: cannot open '"
      + cnf_file + "': " + std::strerror(errno));
  {
    CMSat::DimacsParser<CMSat::StreamBuffer<FILE*, CMSat::FN>, ArjunNS::SimplifiedCNF>
      parser(&cnf, nullptr, 0, fg);
    if (!parser.parse_DIMACS(in, true)) {
      std::fclose(in);
      throw std::runtime_error("compile_to_ganak_into: DIMACS parse error in '"
        + cnf_file + "'");
    }
  }
  std::fclose(in);

  if (!cnf.get_sampl_vars_set()) {
    std::vector<uint32_t> all;
    all.reserve(cnf.nVars());
    for (uint32_t i = 0; i < cnf.nVars(); ++i) all.push_back(i);
    cnf.set_sampl_vars(all);
  }

  GanakInt::CounterConfiguration conf;
  conf.verb              = 0;
  conf.do_chronobt       = 0;
  conf.do_use_sat_solver = 0;
  conf.first_restart     = INT_MAX;
  conf.do_buddy          = 0;

  Ganak counter(conf, fg);
  counter.new_vars(cnf.nVars());

  std::set<uint32_t> indeps, opt_indeps;
  for (uint32_t v : cnf.sampl_vars)     indeps.insert(v + 1);
  for (uint32_t v : cnf.opt_sampl_vars) opt_indeps.insert(v + 1);
  if (opt_indeps.empty()) opt_indeps = indeps;

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
