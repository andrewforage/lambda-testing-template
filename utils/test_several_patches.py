"""
Copy patches to /tmp/ and call POST individually


By default, it'll call valid patches in task2 and task3.
Otherwise, include an argument containing the list of patches to be tested. The argument should have no spaces and be comma separated.

Examples:
python utils/test_several_patches.py sample_patches/task2/mod2_anish.patch,sample_patches/task2/solution2.patch
python utils/test_several_patches.py sample_patches/task3/mod3_connor.patch,sample_patches/task3/mod3_azim.patch,sample_patches/task3/mod3_sasilyu.patch,sample_patches/task3/mod3_sebastian.patch

"""


import os
import sys

def test(p):
    os.system("python utils/cp_patch.py " + p)
    os.system("curl -X POST http://localhost:5000/test")

if __name__ == '__main__':
    t2 = 'mod2_simon.patch','mod2_brian.patch','solution2.patch','mod2_sasilyu.patch'
    t2 = ["sample_patches/task2/" + x for x in t2]
    t3 = 'mod3_azim.patch','mod3_sasilyu.patch','solution3.patch','mod3_connor.patch','mod3_sebastian.patch'
    t3 = ["sample_patches/task3/" + x for x in t3]

    patches = t2 + t3

    for p in patches:
        test(p)
