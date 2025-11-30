import os
import sys

# Default list of required files
DEFAULT_REQUIRED_FILES = ["README.md", ".gitignore"]

def check_required_files(required_files=None):
    """
    Check that each file in required_files exists in the current directory.
    
    Returns:
        0 if all required files exist
        1 if any are missing
    """
    if required_files is None:
        required_files = DEFAULT_REQUIRED_FILES
        
    missing_files = []
    
    for filename in required_files:
        if not os.path.isfile(filename):
            missing_files.append(filename)
            
    if missing_files:
        print("Missing required files:")
        for f in missing_files:
            print(f" -", f)
        # Non-zero exit code = GitHub Actions step FAIL
        return 1
    
    # "Pass silently" - but a small message is ok for humans
    print("All required files are present.")
    return 0


if __name__ == "__main__":
    exit_code = check_required_files()
    sys.exit(exit_code)