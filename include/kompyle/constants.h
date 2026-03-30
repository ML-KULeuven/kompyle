// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#pragma once

#include <arjun/arjun.h>

#include <cstdint>
#include <string>

struct ArjunOptions {
  int arjun_verb = 0;
  int do_arjun = 1;
  int arjun_gates = 1;
  int do_pre_backbone = 0;
  int do_probe_based = 1;
  int arjun_simp_level = 2;
  int arjun_backw_maxc = 20000;
  int arjun_oracle_find_bins = 6;
  double arjun_cms_glob_mult = -1.0;
  int arjun_extend_max_confl = 1000;
  int arjun_extend_ccnr = 0;
  int arjun_autarkies = 0;

  int do_puura = 1;
  uint32_t arjun_further_min_cutoff = 10;
  int bits_jobs = 10;
  int num_threads = 1;
  int strip_opt_indep = 0;

  std::string debug_arjun_cnf;
  ArjunNS::Arjun::ElimToFileConf etof_conf;
  ArjunNS::SimpConf simp_conf;
};
