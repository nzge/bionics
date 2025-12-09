"""
Metabolic Analysis Module
Analyzes metabolic cost using muscle metabolics probes
"""
import opensim as osim
import os


def add_metabolic_probes(model_path, output_model_path, 
                        probe_type='Umberger2010'):
    """
    Add metabolic probes to model
    
    Args:
        model_path (str): Path to input model
        output_model_path (str): Path to save model with probes
        probe_type (str): 'Umberger2010' or 'Bhargava2004'
    
    Returns:
        str: Path to model with metabolic probes
    """
    model = osim.Model(model_path)
    muscle_set = model.getMuscles()
    
    # Add individual muscle probes
    for i in range(muscle_set.getSize()):
        muscle = muscle_set.get(i)
        muscle_name = muscle.getName()
        
        if probe_type == 'Umberger2010':
            probe = osim.Umberger2010MuscleMetabolicsProbe()
        elif probe_type == 'Bhargava2004':
            probe = osim.Bhargava2004MuscleMetabolicsProbe()
        else:
            raise ValueError(f"Unknown probe type: {probe_type}")
        
        probe.setName(f"{muscle_name}_metabolics")
        probe.addMuscle(muscle_name, 1.0)
        model.addProbe(probe)
    
    # Add whole-body probe
    if probe_type == 'Umberger2010':
        whole_body_probe = osim.Umberger2010MuscleMetabolicsProbe()
    else:
        whole_body_probe = osim.Bhargava2004MuscleMetabolicsProbe()
    
    whole_body_probe.setName("whole_body_metabolics")
    
    for i in range(muscle_set.getSize()):
        muscle_name = muscle_set.get(i).getName()
        whole_body_probe.addMuscle(muscle_name, 1.0)
    
    model.addProbe(whole_body_probe)
    
    # Save model
    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    model.finalizeConnections()
    model.printToXML(output_model_path)
    
    print(f"✓ Metabolic probes added: {output_model_path}")
    return output_model_path


def analyze_metabolics(model_with_probes_path, states_file, output_dir):
    """
    Analyze metabolic cost from simulation states
    
    Args:
        model_with_probes_path (str): Model with metabolic probes
        states_file (str): States file (from CMC or forward simulation)
        output_dir (str): Output directory for metabolics results
    
    Returns:
        str: Path to metabolics results file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    model = osim.Model(model_with_probes_path)
    
    # Create analysis tool
    analyze_tool = osim.AnalyzeTool()
    analyze_tool.setModel(model)
    analyze_tool.setStatesFileName(states_file)
    
    # Add ProbeReporter
    probe_reporter = osim.ProbeReporter()
    probe_reporter.setName("ProbeReporter")
    analyze_tool.getAnalysisSet().cloneAndAppend(probe_reporter)
    
    # Set time range from states
    states_storage = osim.Storage(states_file)
    analyze_tool.setInitialTime(states_storage.getFirstTime())
    analyze_tool.setFinalTime(states_storage.getLastTime())
    
    analyze_tool.setResultsDir(output_dir)
    analyze_tool.run()
    
    output_file = os.path.join(output_dir, "ProbeReporter_probes.sto")
    print(f"✓ Metabolic analysis complete: {output_file}")
    return output_file


def calculate_metabolic_cost(metabolics_file):
    """
    Calculate summary statistics from metabolics file
    
    Args:
        metabolics_file (str): Path to metabolics results (.sto)
    
    Returns:
        dict: Summary statistics (mean, total, etc.)
    """
    storage = osim.Storage(metabolics_file)
    
    # Get whole body metabolics column
    wb_index = storage.getColumnLabels().findIndex("whole_body_metabolics")
    
    if wb_index < 0:
        print("⚠ Warning: whole_body_metabolics not found")
        return {}
    
    # Extract data
    time_vec = osim.ArrayDouble()
    storage.getTimeColumn(time_vec)
    
    total_time = time_vec.get(time_vec.size() - 1) - time_vec.get(0)
    
    # Calculate mean power
    mean_power = storage.getColumnMean(wb_index)
    
    # Total energy (integrate power over time)
    total_energy = mean_power * total_time
    
    results = {
        'mean_power_W': mean_power,
        'total_energy_J': total_energy,
        'duration_s': total_time,
    }
    
    print(f"✓ Mean metabolic power: {mean_power:.2f} W")
    print(f"✓ Total metabolic energy: {total_energy:.2f} J")
    
    return results

