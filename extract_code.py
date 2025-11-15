import os
import sys
# --- CONFIGURATION ---
# Add any file extensions you want to include
INCLUDE_EXTENSIONS = {
    # Python/Django
    '.py',
    '.html',
    '.css',
    '.md',
    '.txt',
    '.toml',
    '.yaml',
    '.yml',
    # Vite/Frontend
    '.js',
    '.jsx',
    '.ts',
    '.tsx',
    '.vue',
    '.svelte',
    '.scss',
    '.sass',
    '.less',
    '.json',
}
# Add any specific filenames you want to include (even if their extension isn't listed)
INCLUDE_FILENAMES = {
    'requirements.txt',
    'Dockerfile',
    'docker-compose.yml',
    '.gitignore',
    'manage.py',
    'vite.config.js',
    'vite.config.ts',
    'tailwind.config.js',
    'postcss.config.js',
}
# Add directory names to completely skip
EXCLUDE_DIRS = {
    'node_modules',
    'venv',
    '.venv',
    'env',
    '.git',
    '__pycache__',
    'dist',
    'build',
    'media',
    'staticfiles',
    '.pytest_cache',
    '.mypy_cache',
    '.idea',
    '.vscode',
}
# Add file prefixes or full names to skip
EXCLUDE_FILES_PREFIX = {
    '.env', # Excludes .env, .env.local, .env.production, etc.
}
EXCLUDE_FILES_SUFFIX = {
    '.log',
    '.sqlite3',
    '.pyc',
    '.pyo',
    '.DS_Store',
    '.local',
    '.swp',
}
# --- END CONFIGURATION ---
def is_excluded(path, root):
    """Checks if a file or directory should be excluded."""
    # Get the relative path components
    rel_path = os.path.relpath(path, root)
    components = rel_path.split(os.sep)
    
    # Check if any directory component is in EXCLUDE_DIRS
    for component in components:
        if component in EXCLUDE_DIRS:
            return True
    
    filename = os.path.basename(path)
    
    # Check for excluded file prefixes
    for prefix in EXCLUDE_FILES_PREFIX:
        if filename.startswith(prefix):
            return True
            
    # Check for excluded file suffixes
    for suffix in EXCLUDE_FILES_SUFFIX:
        if filename.endswith(suffix):
            return True
    return False
def extract_project_code(project_dir, output_file):
    """
    Walks the project directory and writes the content of included files
    to the output file.
    """
    count = 0
    if not os.path.isdir(project_dir):
        print(f"Error: Project directory not found: {project_dir}")
        return
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # os.walk(..., topdown=True) allows us to prune directories
            for root, dirnames, filenames in os.walk(project_dir, topdown=True):
                
                # Prune excluded directories from further traversal
                dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    
                    # Check if the file itself is in an excluded path
                    if is_excluded(file_path, project_dir):
                        continue
                    # Get file extension
                    _name, file_ext = os.path.splitext(filename)
                    
                    # Check if file should be included
                    if (file_ext.lower() in INCLUDE_EXTENSIONS or
                        filename in INCLUDE_FILENAMES):
                        
                        relative_path = os.path.relpath(file_path, project_dir)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                content = infile.read()
                            
                            outfile.write(f"--- START OF {relative_path} ---\n\n")
                            outfile.write(content)
                            outfile.write(f"\n\n--- END OF {relative_path} ---\n\n")
                            
                            print(f"Added: {relative_path}")
                            count += 1
                        
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")
    except IOError as e:
        print(f"Error writing to output file {output_file}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    print(f"\nDone. Extracted {count} files to {output_file}")
if __name__ == "__main__":
    import datetime
    if len(sys.argv) > 1:
        # Use command-line arguments if provided
        project_path = sys.argv[1]
        output_path = sys.argv[2] + f"backend_content_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt" if len(sys.argv) > 2 else f"backend_content_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
    else:
        # Otherwise, prompt the user
        print("--- Project Code Extractor ---")
        project_path = input("Enter the full path to your Vite + Django project root: ")
        output_path = f"backend_content_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
    # Normalize paths
    project_path = os.path.abspath(project_path)
    output_path = os.path.abspath(output_path)
    extract_project_code(project_path, output_path)