# perpetual


## Python implementations of perpetual Voting Rules

Perpetual voting rules [1] are voting rules that take the history of previous
decisions into account. Due to this additional information, perpetual voting
rules offer temporal fairness guarantees that cannot be achieved in singular decisions.
In particular, such rules may enable minorities to have a fair (proportional)
influence on the decision process and thus foster long-term participation of minorities.
Further details can be found in [1], in particular a description of all
implemented rules.

## Example

The following code computes the Proportional Approval Voting (PAV) rule for a profile with 6 voters and 5 candidates.

```python
from preferences import Profile
import rules_approval

profile = Profile(5)
profile.add_preferences([[0,1,2], [0,1], [0,1], [1,2], [3,4], [3,4]])
committeesize = 3
print rules_approval.compute_pav(profile, committeesize, ilp=False)
```
The output is 
```
[[0, 1, 3], [0, 1, 4]]
```
which corresponds to the two committees {0,1,3} and {0,1,4}. Further examples can be found in [examples.py](examples.py).

## Comments

* This module requires Python 2.7.
* Some functions use fractions (e.g., `compute_seqphragmen`). These compute significantly faster if the module [gmpy2](https://gmpy2.readthedocs.io/) is available. If gmpy2 is not available, the much slower Python module [fractions](https://docs.python.org/2/library/fractions.html) is used.


## References

[1] 
