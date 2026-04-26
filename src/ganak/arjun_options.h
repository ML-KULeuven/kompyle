// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#ifndef SRC_GANAK_ARJUN_OPTIONS_H_
#define SRC_GANAK_ARJUN_OPTIONS_H_

#include <cstdint>
#include <string>

#include "arjun/arjun.h"

#include "kompyle/options.h"

namespace kmpyl {

// ---------------------------------------------------------------------------
// Arjun Configuration
// ---------------------------------------------------------------------------

struct ArjunConf {
  int arjun_verb              = 0;
  int do_arjun                = 1;
  int arjun_gates             = 1;
  int do_pre_backbone         = 0;
  int do_probe_based          = 1;
  int arjun_simp_level        = 2;
  int arjun_backw_maxc        = 20000;
  int arjun_oracle_find_bins  = 6;
  double arjun_cms_glob_mult  = -1.0;
  int arjun_extend_max_confl  = 1000;
  int arjun_extend_ccnr       = 0;
  int arjun_autarkies         = 0;

  int do_puura                         = 1;
  uint32_t arjun_further_min_cutoff    = 10;
  int bits_jobs                        = 10;
  int num_threads                      = 1;
  int strip_opt_indep                  = 0;

  std::string debug_arjun_cnf;
  ArjunNS::Arjun::ElimToFileConf etof_conf;
  ArjunNS::SimpConf              simp_conf;
};

inline ArjunConf MakeArjunConf(const ArjunOptions& pub) {
  ArjunConf conf;
  conf.arjun_verb             = pub.verb;
  conf.do_arjun               = pub.do_arjun              ? 1 : 0;
  conf.arjun_gates            = pub.arjun_gates           ? 1 : 0;
  conf.do_pre_backbone        = pub.do_pre_backbone       ? 1 : 0;
  conf.do_probe_based         = pub.do_probe_based        ? 1 : 0;
  conf.arjun_simp_level       = pub.arjun_simp_level;
  conf.arjun_backw_maxc       = pub.arjun_backw_maxc;
  conf.arjun_oracle_find_bins = pub.arjun_oracle_find_bins;
  conf.arjun_cms_glob_mult    = pub.arjun_cms_glob_mult;
  conf.arjun_extend_max_confl = pub.arjun_extend_max_confl;
  conf.arjun_extend_ccnr      = pub.arjun_extend_ccnr      ? 1 : 0;
  conf.arjun_autarkies        = pub.arjun_autarkies        ? 1 : 0;
  conf.do_puura               = pub.do_puura               ? 1 : 0;
  conf.arjun_further_min_cutoff = pub.arjun_further_min_cutoff;
  conf.num_threads            = pub.num_threads;
  conf.strip_opt_indep        = pub.strip_opt_indep        ? 1 : 0;
  conf.etof_conf.all_indep    = pub.all_indep;
  return conf;
}

}  // namespace kmpyl

#endif  // SRC_GANAK_ARJUN_OPTIONS_H_
