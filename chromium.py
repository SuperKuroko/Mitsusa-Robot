import sys
from playwright.__main__ import main
sys.argv = ['', 'install', 'chromium']
try:
    main()
except SystemExit:
    pass
