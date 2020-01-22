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

* This module requires Python 2.7 or 3.6+.
* It also requires the packages [gmpy2](https://gmpy2.readthedocs.io/), future, numpy, scipy and matplotlib (see [requirements.txt](requirements.txt)).
* A simple example can be found in [examples/examples.py](examples/examples.py).
* The code for running the numerical simulations in [1] is contained in [experiments/experiments_aaai.py](experiments/experiments_aaai.py).
* For the code in [experiments/experiments_incomplete.py](experiments/experiments_incomplete.py) and [experiments/experiments_complete.py](experiments/experiments_complete.py) data from [https://www.dbai.tuwien.ac.at/proj/sudema/data/data.zip](https://www.dbai.tuwien.ac.at/proj/sudema/data/data.zip) is required. Simply download the tsoi collection and extract it into this directory. 

## Contributors

The following people have contributed code to this package and provided help with technical and scientific questions (in alphabetic order): [Benjamin Krenn](https://github.com/benjaminkrenn), [Martin Lackner](http://martin.lackner.xyz/).

## References

[1] Martin Lackner. Perpetual Voting: Fairness in Long-Term Decision Making. Proceedings of AAAI 2020, 2020. http://martin.lackner.xyz/publications/perpetual.pdf
