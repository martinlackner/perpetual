# perpetual


## Python implementations of perpetual voting rules

Perpetual voting rules [1] are voting rules that take the history of previous
decisions into account. Due to this additional information, perpetual voting
rules offer temporal fairness guarantees that cannot be achieved in singular decisions.
In particular, such rules may enable minorities to have a fair (proportional)
influence on the decision process and thus foster long-term participation of minorities.
Further details can be found in [1], in particular a description of all
implemented rules.

## Comments

* This module requires Python 2.7 and [gmpy2](https://gmpy2.readthedocs.io/).
* A simple example can be found in [examples.py](examples.py).
* The code for running the numerical simulations in [1] are contained in [experiments.py](experiments.py).

## References

[1] Martin Lackner. Perpetual Voting: Fairness in Long-Term Decision Making. Proceedings of AAAI 2020, 2020. http://martin.lackner.xyz/publications/perpetual.pdf
