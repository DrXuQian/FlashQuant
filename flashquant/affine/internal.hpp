#pragma once
#include "api.h"
#include <stdexcept>

namespace quactlize::affine {

struct Plan {
    virtual int run(void*) = 0;
    virtual ~Plan() = default;
};

struct Entry {
    qwa_config_v1 config;
    qwa_info_v1 (*query)(qwa_problem_v1 const&);
    Plan* (*prepare)(qwa_problem_v1 const&, qwa_buffers_v1 const&);
    int zero_mode=0;
};

extern Entry const entries[];
extern int const entry_count;
int default_config(qwa_problem_v1 const&);

inline void require(bool valid, char const* message) {
    if (!valid) throw std::invalid_argument(message);
}

}
