# debug.py
from utils import MathProblemManager

try:
    from utils import PrintOptionsDialog
    print("PrintOptionsDialog está en utils")
except ImportError as e:
    print(f"Error importando PrintOptionsDialog: {str(e)}")
