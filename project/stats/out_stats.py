import pstats
import sys
from pstats import SortKey

#filename = "ga_profile.txt"
filename = sys.argv[1]
p = pstats.Stats(filename)
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)
