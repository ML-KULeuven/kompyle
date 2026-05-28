// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Per-operation counters for d4 calls.

#ifndef SRC_D4_D4_STATS_H_
#define SRC_D4_D4_STATS_H_

#include <atomic>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <string>
#include <utility>

namespace kmpyl {

struct D4OpStats {
  std::string name;

  std::atomic<uint64_t> n_top{0},    ns_top{0};
  std::atomic<uint64_t> n_bottom{0}, ns_bottom{0};
  std::atomic<uint64_t> n_branch{0}, ns_branch{0};
  std::atomic<uint64_t> n_add{0},    ns_add{0};
  std::atomic<uint64_t> n_mul{0},    ns_mul{0};

  std::atomic<uint64_t> n_lit_node{0}, ns_lit_node{0};
  std::atomic<uint64_t> n_taut{0},     ns_taut{0};

  explicit D4OpStats(std::string n) : name(std::move(n)) {}

  void reset() {
    n_top = 0;       ns_top = 0;
    n_bottom = 0;    ns_bottom = 0;
    n_branch = 0;    ns_branch = 0;
    n_add = 0;       ns_add = 0;
    n_mul = 0;       ns_mul = 0;
    n_lit_node = 0;  ns_lit_node = 0;
    n_taut = 0;      ns_taut = 0;
  }

  void print() const {
    auto avg = [](uint64_t ns, uint64_t n) -> uint64_t {
      return n ? ns / n : 0;
    };
    std::cout
        << "[D4OpStats:" << name << "]\n"
        << "  top    : " << n_top    << " calls, " << ns_top    << " ns total"
        << " (" << avg(ns_top,    n_top)    << " ns/call)\n"
        << "  bottom : " << n_bottom << " calls, " << ns_bottom << " ns total"
        << " (" << avg(ns_bottom, n_bottom) << " ns/call)\n"
        << "  branch : " << n_branch << " calls, " << ns_branch << " ns total"
        << " (" << avg(ns_branch, n_branch) << " ns/call)\n"
        << "  add    : " << n_add    << " calls, " << ns_add    << " ns total"
        << " (" << avg(ns_add,    n_add)    << " ns/call)\n"
        << "  mul    : " << n_mul    << " calls, " << ns_mul    << " ns total"
        << " (" << avg(ns_mul,    n_mul)    << " ns/call)\n"
        << "  lit    : " << n_lit_node << " calls, " << ns_lit_node
        << " ns total (" << avg(ns_lit_node, n_lit_node) << " ns/call)\n"
        << "  taut   : " << n_taut    << " calls, " << ns_taut    << " ns total"
        << " (" << avg(ns_taut,   n_taut)   << " ns/call)\n";
  }
};

extern D4OpStats g_d4_stats_circuit;
extern D4OpStats g_d4_stats_count;

class D4ScopedTimer {
 public:
  explicit D4ScopedTimer(std::atomic<uint64_t>& acc)
      : acc_(acc), t0_(std::chrono::steady_clock::now()) {}

  ~D4ScopedTimer() {
    acc_ += static_cast<uint64_t>((std::chrono::steady_clock::now() - t0_).count());
  }

  D4ScopedTimer(const D4ScopedTimer&) = delete;
  D4ScopedTimer& operator=(const D4ScopedTimer&) = delete;

 private:
  std::atomic<uint64_t>& acc_;
  std::chrono::steady_clock::time_point t0_;
};

}  // namespace kmpyl

#endif  // SRC_D4_D4_STATS_H_

