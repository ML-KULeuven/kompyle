#pragma once
#include <atomic>
#include <chrono>
#include <iostream>
#include <string>

struct FieldStats {
    std::string name;
    std::atomic<uint64_t> n_gen_dup{0}, n_dup{0};
    std::atomic<uint64_t> n_add{0}, n_mul{0}, n_zero{0}, n_one{0};
    std::atomic<uint64_t> ns_gen_dup{0}, ns_dup{0};
    std::atomic<uint64_t> ns_add{0}, ns_mul{0}, ns_zero{0}, ns_one{0};
    std::atomic<uint64_t> n_lit_field{0}, ns_lit_field{0};

    explicit FieldStats(std::string n) : name(std::move(n)) {}

    void reset() {
        n_gen_dup = 0;   ns_gen_dup = 0;
        n_dup = 0;       ns_dup = 0;
        n_add = 0;       ns_add = 0;
        n_mul = 0;       ns_mul = 0;
        n_zero = 0;      ns_zero = 0;
        n_one = 0;       ns_one = 0;
        n_lit_field = 0; ns_lit_field = 0;
    }


    void print() const {
        auto avg = [](uint64_t ns, uint64_t n) {
            return n ? ns / n : 0;
        };
        std::cout << "[FieldStats:" << name << "]\n"
            << "  field dup : " << n_dup << " calls, " << ns_dup << " ns total"
            << " (" << avg(ns_dup, n_dup) << " ns/call)\n"
            << "  fgen dup : " << n_gen_dup << " calls, " << ns_gen_dup << " ns total"
            << " (" << avg(ns_gen_dup, n_gen_dup) << " ns/call)\n"
            << "  add : " << n_add << " calls, " << ns_add << " ns total"
            << " (" << avg(ns_add, n_add) << " ns/call)\n"
            << "  mul : " << n_mul << " calls, " << ns_mul << " ns total"
            << " (" << avg(ns_mul, n_mul) << " ns/call)\n"
            << "  zero: " << n_zero << " calls, " << ns_zero << " ns total"
            << " (" << avg(ns_zero, n_zero) << " ns/call)\n"
            << "  one : " << n_one  << " calls, " << ns_one  << " ns total"
            << " (" << avg(ns_one, n_one) << " ns/call)\n";
    }
};

inline FieldStats g_gk_stats_circuit("FCircuit");
inline FieldStats g_gk_stats_count("FCount");
