import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Empty the contents of a folder.')
    parser.add_argument('ellipse_height', help='Height of the ellipse')
    parser.add_argument('mach', help='Mach Number')

    args = parser.parse_args()
    
    h = float(args.ellipse_height)
    M = float(args.mach)
    
    # Read in the data
    if os.path.exists(os.path.join('data', str(h))):
        if os.path.exists(os.path.join('data', str(h), str(M))):
            df = pd.read_csv(os.path.join('data', str(h), str(M)))
            plt.scatter(df['x'], df['y'], marker='x', color='black')
            plt.grid()
            plt.title('h = {}, M = {}'.format(h, M))
            plt.xlim(0, 0.5)
            plt.ylim(0, 0.2)
            plt.show()
        else:
            print('No data for M = {}. in h = {}.'.format(M, h))
    else:
        print('No data for h = {}.'.format(h))

    
if __name__ == '__main__':
    main()