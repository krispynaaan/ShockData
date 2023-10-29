import pandas as pd
import os 
import matplotlib.pyplot as plt

# converting csv data to plots

base_dir = 'data'

for height in os.listdir(base_dir):
  for mach in os.listdir(os.path.join(base_dir, height)):
        df = pd.read_csv(os.path.join(base_dir, height, mach)) # x and y columns
        
        title = f'Height: {height}, Mach: {mach}'
        
        # plot
        plt.figure(figsize=(10, 10))
        plt.title(title)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid()
        plt.scatter(df['x'], df['y'], marker="x", color="0")
        plt.xlim(0, 0.5)
        plt.ylim(0, 0.2)

        # save to 'plots' folder
        os.makedirs(os.path.join('plots', height), exist_ok=True)
        plt.savefig(os.path.join('plots', height, mach + '.png'))
        
# generating report from plots

import os
from pylatex import Document, Section, Command, Figure, Package
from pylatex.utils import italic, NoEscape

base_dir = 'plots'

doc = Document('plots')
doc.packages.append(Command('title', 'Plots'))
doc.packages.append(Package('float'))

title_page = r"""
\begin{titlepage}      
  \begin{center}
      \includegraphics[width=3cm]{static/td-logo.png}\\[0.5cm]
      {\LARGE Texas A\&M University}\\[2cm]
      %{\color{blue} \rule{\textwidth}{1pt}}
      
      \linespread{1.2}\huge {
          Detached Shock Data for Elliptical Airfoils
      }
      \linespread{1}~\\[2cm]
      
      \includegraphics[width=6cm]{static/plane.png}\\[0.5cm]
      
      {\Large 
          Krishnan Vellore, Anthony Pasala, Carol Geng, Roshan Tayab
      }\\[1cm] 
                  
  \end{center}
\end{titlepage}
"""

doc.append(NoEscape(title_page))


doc.append(NoEscape(r'\tableofcontents'))


# Iterate over the subdirectories in the plots directory
for subdir in os.listdir(base_dir):
    subdir_path = os.path.join(base_dir, subdir)
    # Create a new section for each subdirectory
    with doc.create(Section("Height " + subdir)):
        # Iterate over the images in the subdirectory
        for filename in os.listdir(subdir_path):
            # Add the image to the LaTeX document
            with doc.create(Figure(position='H')) as plot:
                plot.add_image(os.path.join(subdir_path, filename), width='400px')
                plot.add_caption("Mach " + filename.removesuffix('.png'))

# Generate the LaTeX document
doc.generate_pdf('plots', clean=True)
