import sys
import time
from typing import Optional

class ProgressBar:
    """
    A simple progress bar for console output.
    """
    
    def __init__(self, total: int, prefix: str = '', suffix: str = '', decimals: int = 1,
                 length: int = 50, fill: str = '█', print_end: str = "\r"):
        """
        Initialize progress bar.
        
        Args:
            total (int): Total iterations
            prefix (str): Prefix string
            suffix (str): Suffix string
            decimals (int): Decimal places for percentage
            length (int): Character length of bar
            fill (str): Bar fill character
            print_end (str): End character (e.g. "\r", "\r\n")
        """
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end
        self.iteration = 0
        self.start_time = time.time()
    
    def print(self, iteration: Optional[int] = None):
        """
        Print progress bar.
        
        Args:
            iteration (int, optional): Current iteration
        """
        if iteration is not None:
            self.iteration = iteration
        
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (self.iteration / float(self.total)))
        filled_length = int(self.length * self.iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        
        # Calculate elapsed time and estimated time remaining
        elapsed_time = time.time() - self.start_time
        if self.iteration > 0:
            eta = elapsed_time * (self.total / self.iteration - 1)
            time_info = f" | {format_time(elapsed_time)} < {format_time(eta)}"
        else:
            time_info = ""
        
        # Print progress bar
        sys.stdout.write(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}{time_info}{self.print_end}')
        sys.stdout.flush()
        
        # Print new line on complete
        if self.iteration == self.total:
            print()
    
    def increment(self, amount: int = 1):
        """
        Increment progress bar.
        
        Args:
            amount (int): Amount to increment by
        """
        self.iteration = min(self.iteration + amount, self.total)
        self.print()

def format_time(seconds: float) -> str:
    """
    Format time in seconds to human readable string.
    
    Args:
        seconds (float): Time in seconds
    
    Returns:
        str: Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"
