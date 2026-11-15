# November 15 · scheduled review 3

Last week's L5 predicted that checking the emitted high operation together with its residual would expose an assumption the source model missed. On GCC 13.3, the leading Horner sum is fused and its residual is a fused subtract. The new enclosure bounds those operations directly. The two π products used by the last sums are exact throughout the reachable signed-index range. Keep L5 for the next different compiler graph. [Operation mapping](REPRODUCE.md)

Comparing generator output at equal budgets separated a change in sample count from a change in the sampled inputs. Checking existing corpus membership retired a proposed tgamma boundary addition before a duplicate patch was written. Reassess these practices at the fourth scheduled learning review on November 22. No maintainer time-saving estimate is available.
