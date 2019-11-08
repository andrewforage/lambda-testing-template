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
