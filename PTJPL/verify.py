def verify() -> bool:
    """
    Verifies the correctness of the PT-JPL model implementation by comparing
    its outputs to a reference dataset.

    This function loads a known input table and the corresponding expected output table.
    It runs the model on the input data, then compares the resulting outputs to the
    reference outputs for key variables using strict numerical tolerances. If all
    outputs match within tolerance, the function returns True. Otherwise, it prints
    which column failed and returns False.

    Returns:
        bool: True if all model outputs match the reference outputs within tolerance, False otherwise.
    """
    import pandas as pd
    import numpy as np
    from .ECOv002_calval_PTJPL_inputs import load_ECOv002_calval_PTJPL_inputs
    from .process_PTJPL_table import process_PTJPL_table
    import os

    # Load input and output tables
    input_df = load_ECOv002_calval_PTJPL_inputs()
    module_dir = os.path.dirname(os.path.abspath(__file__))
    output_file_path = os.path.join(module_dir, "ECOv002-cal-val-PT-JPL-outputs.csv")
    output_df = pd.read_csv(output_file_path)

    # Run the model on the input table
    model_df = process_PTJPL_table(input_df)

    # Columns to compare (model outputs)
    output_columns = [
        "G_Wm2",
        "Rn_soil_Wm2",
        "LE_soil_Wm2",
        "Rn_canopy_Wm2",
        "PET_Wm2",
        "LE_canopy_Wm2",
        "LE_interception_Wm2",
        "LE_Wm2"
    ]

    # Compare each output column and collect mismatches
    mismatches = []
    for col in output_columns:
        if col not in model_df or col not in output_df:
            mismatches.append((col, 'missing_column', None))
            continue
        model_vals = model_df[col].values
        ref_vals = output_df[col].values
        # Use numpy allclose for floating point comparison
        if not np.allclose(model_vals, ref_vals, rtol=1e-5, atol=1e-8, equal_nan=True):
            # Find indices where values differ
            diffs = np.abs(model_vals - ref_vals)
            max_diff = np.nanmax(diffs)
            idxs = np.where(~np.isclose(model_vals, ref_vals, rtol=1e-5, atol=1e-8, equal_nan=True))[0]
            mismatch_info = {
                'indices': idxs.tolist(),
                'model_values': model_vals[idxs].tolist(),
                'ref_values': ref_vals[idxs].tolist(),
                'diffs': diffs[idxs].tolist(),
                'max_diff': float(max_diff)
            }
            mismatches.append((col, 'value_mismatch', mismatch_info))
    if mismatches:
        print("Verification failed. Details:")
        for col, reason, info in mismatches:
            if reason == 'missing_column':
                print(f"  Missing column: {col}")
            elif reason == 'value_mismatch':
                print(f"  Mismatch in column: {col}")
                print(f"    Max difference: {info['max_diff']}")
                print(f"    Indices off: {info['indices']}")
                print(f"    Model values: {info['model_values']}")
                print(f"    Reference values: {info['ref_values']}")
                print(f"    Differences: {info['diffs']}")
        return False
    return True
