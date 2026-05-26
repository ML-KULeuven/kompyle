#include "d4/d4_stats.h"

namespace kmpyl {

#if defined(__GNUC__) || defined(__clang__)
__attribute__((visibility("default"))) D4OpStats g_d4_stats_circuit("D4KlayCircuit");
__attribute__((visibility("default"))) D4OpStats g_d4_stats_count("D4MpzCounting");
#else
D4OpStats g_d4_stats_circuit("D4KlayCircuit");
D4OpStats g_d4_stats_count("D4MpzCounting");
#endif

}  // namespace kmpyl
