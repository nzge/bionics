import opensim as osim
import os
import json

def create_project_structure(base_dir):
    """
    Create standard OpenSim project directory structure
    Args:
        base_dir (str): Base project directory
    
    Returns:
        dict: Paths to created directories
    """
    dirs = {
        'data': {
            'results': {
                'scaling': os.path.join(base_dir, 'data', 'results', 'scaling'),
                'ik': os.path.join(base_dir, 'data', 'results', 'ik'),
                'id': os.path.join(base_dir, 'data', 'results', 'id'),
                'cmc': os.path.join(base_dir, 'data', 'results', 'cmc'),
                'metabolics': os.path.join(base_dir, 'data', 'results', 'metabolics'),
                'rra': os.path.join(base_dir, 'data', 'results', 'rra'),
            }
        }  
    }

    def make_dirs(d):
        """Recursively create directories from a nested dict"""
        for key, value in d.items():
            if isinstance(value, dict):
                make_dirs(value)
            else:
                os.makedirs(value, exist_ok=True)

    make_dirs(dirs)
    print(f"✓ Project structure created at: {base_dir}")
    return dirs
    

def load_storage_to_dict(storage_file):
    """
    Load OpenSim storage file to dictionary
    
    Args:
        storage_file (str): Path to .sto or .mot file
    
    Returns:
        dict: Data organized by column name
    """
    storage = osim.Storage(storage_file)
    labels = storage.getColumnLabels()
    
    data = {'time': []}
    
    # Initialize columns
    for i in range(labels.size()):
        label = labels.get(i)
        if label != 'time':
            data[label] = []
    
    # Extract data
    for i in range(storage.getSize()):
        state_vector = storage.getStateVector(i)
        data['time'].append(state_vector.getTime())
        
        for j in range(state_vector.getSize()):
            label = labels.get(j + 1)  # +1 to skip 'time'
            data[label].append(state_vector.getData().get(j))
    
    return data


def save_results_summary(output_dir, results_dict):
    """
    Save analysis results summary as JSON
    
    Args:
        output_dir (str): Output directory
        results_dict (dict): Dictionary of results
    
    Returns:
        str: Path to JSON file
    """
    summary_file = os.path.join(output_dir, 'results_summary.json')
    
    with open(summary_file, 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    print(f"✓ Results summary saved: {summary_file}")
    return summary_file


def verify_file_exists(filepath, description="File"):
    """
    Verify file exists and provide helpful error message
    
    Args:
        filepath (str): Path to check
        description (str): Description for error message
    
    Returns:
        bool: True if file exists
    
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"{description} not found: {filepath}\n"
            f"Please check the file path and try again."
        )
    return True