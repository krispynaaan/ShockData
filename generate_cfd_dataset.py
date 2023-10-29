import shutil
import os
import re
import numpy as np
import subprocess
from tqdm import tqdm


def delete_excess_data():
    files = ['0.1', '0.02', '0.04', '0.06', '0.08', '0.12', '0.14', '0.16', '0.18']
    for file in files:
        if os.path.exists(file):
            shutil.rmtree(file)

def generate_block_mesh(h):
    file_name = os.path.join('system', 'blockMeshDict')
    with open(file_name, 'r') as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if 'arc' in lines[i]:
            pattern = r'(arc [^\s]+ [^\s]+ \()([^)]+)(\))'

            def replace(match):
                inside_parentheses = match.group(2).split()
                if len(inside_parentheses) >= 2:
                    inside_parentheses[1] = str(h)
                updated_inside_parentheses = ' '.join(inside_parentheses)
                return match.group(1) + updated_inside_parentheses + match.group(3)

            result = re.sub(pattern, replace, lines[i])
            lines[i] = result
            
    with open(file_name, 'w') as f:
        f.writelines(lines)


def generate_mach_numbers(n):
    M_range = np.linspace(1.3, 5, n)
    return M_range

def generate_ellipse_heights(n):
    h_range = np.linspace(0.005, 0.01, n)
    return h_range

def generate_freestream_mach_number(M):
    file_name = os.path.join('0', 'U')
    
    with open(file_name, 'r') as f:
        lines = f.readlines()
        
    for i in range(len(lines)):
        if 'uniform' in lines[i]:
            pattern = r'((internalField|value)\s+uniform\s*\()([^)]+)(\))'

            def replace(match):
                inside_parentheses = match.group(3).split()
                if inside_parentheses:
                    inside_parentheses[0] = str(M)
                updated_inside_parentheses = ' '.join(inside_parentheses)
                return match.group(2) + ' uniform (' + updated_inside_parentheses + match.group(4)

            result = re.sub(pattern, replace, lines[i])
            lines[i] = result
            
    with open(file_name, 'w') as f:
        f.writelines(lines)
        
def update_mesh():
    subprocess.run("blockMesh > logs/dataset_generator_blockMesh.LOG", shell=True)

def run_openfoam():
    subprocess.run("rhoCentralFoam > logs/dataset_generator_foamRun.LOG", shell=True)
    subprocess.run("postProcess -func writeCellCentres > logs/dataset_generator_writeCentres.LOG", shell=True)
    
def read_pressure(file_name):
    pressure = []
    is_value = False
    with open(file_name, 'r') as f:
        for line in f:
            if '(' in line:
                is_value = True
            elif ')' in line:
                is_value = False
            elif is_value:
                pressure.append(float(line))
                
    return np.array(pressure)


def read_coordinates(file_name):
    coordinates = []
    with open(file_name, 'r') as f:
        for line in f:
            if '(' in line and ')' in line:
                values = map(float, line.strip("()\n").split())
                coordinates.append(tuple(values))
            elif ')' in line:
                break
                
    return np.array(coordinates)

def generate_data_file(h, M):
    cords = read_coordinates(os.path.join('0.2', 'C'))
    pressure = read_pressure(os.path.join('0.2', 'p'))
    x = cords[:, 0]
    y = cords[:, 1]
    cell_y = 40

    delta_p_max = [0] * cell_y * 3
    delta_p_max_loc = [(0, 0)] * cell_y * 3
    p_max = [0] * cell_y * 3

    row = 0

    last_x_val = -1
    for i in range(len(pressure) - 2):
        if x[i] <= last_x_val:
            row += 1
        if pressure[i+1] - pressure[i] > delta_p_max[row] and pressure[i+1] > p_max[row] and not(x[i] > 0.3 and y[i] < 0.01):
            p_max[row] = pressure[i+1]
            delta_p_max[row] = pressure[i+1] - pressure[i]
            delta_p_max_loc[row] = (x[i], y[i])
        last_x_val = x[i]
        
    delta_p_max_loc = [item for item in delta_p_max_loc if (item[0] != x[-2] and item[0] != x[-1] and item[0] != 0)]

    delta_p_max_loc = sorted(delta_p_max_loc, key=lambda x: x[0])
    x_values, y_values = zip(*delta_p_max_loc)
    
    with open(os.path.join('data', str(h), str(M)), 'w') as f:
        f.write('x,y\n')
        for i in range(len(x_values)):
            f.write('{},{}\n'.format(x_values[i], y_values[i]))
            
    shutil.rmtree('0.2')

M_n = 100
h_n = 10

for h in tqdm(generate_ellipse_heights(h_n)):
    h = round(h, 4)
    
    os.mkdir(os.path.join('data', str(h)))
    generate_block_mesh(h)
    update_mesh()
    
    for M in generate_mach_numbers(M_n):
        M = round(M, 2)
        
        try:
            generate_freestream_mach_number(M)
            run_openfoam()
            delete_excess_data()
            generate_data_file(h, M)
             
        except:
            print('Error occured for M = {}, h = {}'.format(M, h))
            if os.path.exists('0.2'):
                shutil.rmtree('0.2')
            
            continue
            
        print('Generated dataset for M = {}, h = {}'.format(M, h))
    
