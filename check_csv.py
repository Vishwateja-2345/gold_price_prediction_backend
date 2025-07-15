import pandas as pd
import os

try:
    print('Checking CSV file...')
    csv_path = 'data/gold_data.csv'
    print('File exists:', os.path.exists(csv_path))
    print('File size:', os.path.getsize(csv_path) if os.path.exists(csv_path) else 'N/A')
    
    # Try to read with skipping bad lines
    df = pd.read_csv(csv_path, on_bad_lines='skip')
    print('CSV loaded with skipping bad lines')
    print('Columns:', list(df.columns))
    print('Shape:', df.shape)
    print('First 3 rows:')
    print(df.head(3))
    
    # Check line 513
    with open(csv_path, 'r') as f:
        lines = f.readlines()
        print('\nTotal lines:', len(lines))
        if len(lines) >= 513:
            print('Line 513:', lines[512].strip())
        else:
            print('File has fewer than 513 lines')
            
except Exception as e:
    print('Error:', e)