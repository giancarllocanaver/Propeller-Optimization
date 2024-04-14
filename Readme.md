# **Propeller Optimization Tool** :airplane:

## *What is it?*

This tool was developed to optimize the propulsion efficiency of aeronautical propellers. Aeronautical propellers have been used as the main form of propulsion in many types of aircraft, for over 70 years. Propellers with high propulsion efficiency can reduce the emissions of $CO_2$ in the cruise flight.

For optimizing the propulsion efficiency, this application needs an input description of the propeller, such as the initial airfoil used, the flight condition, and the number of blades. After taking this information, the application tries to modify the airfoils presented along each blade section, in an iterative process, aiming to obtain a propeller with better propulsion efficiency.

## *Table of contents*

- [Theorical background](#blue_book-theorical-background)

- [Architecture and tools](#hammer-architecture-and-tools)

- [Installation](#dvd-installation)

- [Usage](#rocket-usage)

- [References](#microscope-references)

### :blue_book: Theorical background

#### **1. Optimization problem**

Any optimization problem tries to obtain the best solution for a given objective. This objective is always a function, dependent on the problem variables, which can be maximized or minimized; in other words, this function is called the objective function.

In most optimization problems, the variables have certain limits of values since a combination of variables could lead to an impracticable solution for the problem. For limiting these values, new expressions are proposed, called constraints.

A nice introduction to optimization can be found in the following article from medium [``Optimization introduction``](https://medium.com/insiderfinance/optimization-for-beginners-optimization-for-beginners-a-guide-to-solving-optimization-problems-ae2192f9b15d)

#### **2. Particle Swarm Optimization (PSO)**

This optimization algorithm is based on the existence of intelligence in bird migrations, which can be decomposed into global intelligence (the intelligence of all birds together) and local intelligence (the intelligence of each bird), all of them together for successful movements. Each bird in the algorithm is called a particle, representing a possible solution for the problem, with its variables and objective value. This algorithm was chosen as the optimizer due to its non-linearity convergence, which is the type of problem when working with airfoils and propellers.

The iteration process begins with some starting variables, which are updated according to the algorithm proceeds, as illustrated in the following equation:

$$X_{k+1}=X_k + V_{k+1} \cdot \Delta t$$

where $X_k$ is the variables in the $k$ iteration step, $V_k$ is the velocity associated to the movements, and $\Delta t$ is the step difference per iteration. The next velocity term can be calculated as:

$$V_{k+1}=\omega V_k + c_1 r_1 \frac{p_{best} - X_k}{\Delta t} + c_2 r_2 \frac{g_{best} - X_k}{\Delta t}$$

where $c_1$, $c_2$, $r_1$ and $r_2$ are hypermarameters associated; $p_{best}$ is the best particle variables for each particle, and $g_{best}$ is the best particle variables of all particles.

A better understanding of the algorithm can be found in the Kennedy and Eberhart original article: ``KENNEDY, J.; EBERHART, R. Particle swarm optimization. Proceedings of ICNN’95 - International Conference on Neural Networks, 1995``.

#### **3. Optimization variables and objective function**

The objective function of this tool is to maximize the propulsion efficiency. According to El-Sayed, 2017, the propulsion efficiency can be obtained in terms of the traction ($C_T$) and torque ($C_q$) coefficients, and the advance rate ($J$) of the propeller, thus, it can be written as:

$$F.O = max (J \frac{C_T}{C_q})$$

Furthermore, the optimization variables, $C_T$ and $C_q$, depend on the infinity airfoils shape along the blade. As it is almost impossible to consider the contribution of all airfoil sections, thus, for calculating the optimization variables along the iteration process, was utilized: the Blade Element Theory, which discretizes the blade in some airfoil sections, and contributes to lift and drag for the blade; and the xfoil software, which calculates the airfoil contribution in terms of lift, $C_l$ coefficient, and drag, $C_d$ coefficient.

Changing these airfoil shapes results in different propellers or different possibilities of solutions. So, for modifying the shapes, the conception of a Bezier Curve was used; in a nutshell, it takes the spline of the airfoil and obtains some points (A, B, and P points), which can be easily changed to create a new geometry. Thus, a movement value in a specific point of A was utilized as the main variable in the optimization variables, which changes the aerodynamic characteristics of the airfoil, and as a consequence, changes $C_T$ and $C_q$ coefficients.

A better understanding of the Bezier Curves and the Blade Element Theory can be found in the next links:

- [``Bézier Curve``](https://omaraflak.medium.com/b%C3%A9zier-curve-bfffdadea212)

- [``The Blade Element Theory``](https://www.aerodynamics4students.com/propulsion/blade-element-propeller-theory.php)

### :hammer: Architecture and tools

```
main.py
src/
|-- data_modules/
    |-- data_reader.py
    |-- data_structures.py
    |-- data_validation.py
|-- utilities/
    |-- airfoil_creation.py
    |-- constants.py
    |-- custom_logger.py
    |-- exceptions.py
    |-- geometry_management.py
    |-- xfoil_management.py
|-- blade_element_theory.py
|-- objective_function.py
|-- optimizer.py
|-- output_process.py
|-- pipelines.py
processing/
|-- execution_steps/
|-- inputs/
    |-- default-input.json
|-- outputs/
|-- xfoil_instances/
    |-- xfoil.exe
INSTALL/
|-- requirements1.bat
|-- requirements2.bat
```

| File/Folder | Description |
| --- | --- |
| main.py | Main file used for executing the propeller optimization. |
| data_reader.py | Module responsible for reading the input file, placed in processing/inputs directory. |
| data_structures.py | Data structures used in the project. |
| data_validation.py | Module responsible for validating the input data correcty. |
| airfoil_creation.py | Module responsible for creating new NACA airfoils and reading airfoils P points placed in the input file. |
| constants.py | The main constants used along the application. |
| custom_logger.py | Module intended to create a new log object, for creating the processing log. |
| exceptions.py | Specific exception classes which were used in the application. |
| geometry_management.py| Implementation of the bezier process for modifying the airfoil spline. |
| xfoil_management.py | Module responsible for executing the xfoil along the iteration process. |
| blade_element_theory.py | Implementation of the Blade Element Theory for obtaining the objective function value. |
| objective_function.py | Module responsible for managing all the methods for calculating properlly the objective function. |
| optimizer.py | Implementation of the PSO algorithm. |
| output_process.py | Module responsible for generating all the outputs of the optimization. |
| pipelines.py | Module responsible for executing  the main pipeline, which will optimize the propeller efficiency. |
| processing/ | Directory for storaging all the files needed for optimization. |
| inputs/ | Directory where the input files are stored. |
| default-input.json | Default input in json extension. |
| outputs/ | Directory where the outputs are stored, by the input filename. |
| xfoil_instances/ | Folder where the main instance of xfoil is executed. |
| INSTALL/ | Directory where the installation files are stored. |

### :dvd: Installation

For installing the dependencies and executing the tool, it is necessary first to have installed the miniconda3 software or have an individual virtual environment for installing the library's dependencies.

#### 1. Installing with miniconda3

If using miniconda3 and Windows, two '.bat' files can be executed for creating the virtual environment and installing the dependencies. It is just to run the first one, and then, the second one.

#### 2. Installing packages with pip

If using a virtual pre-configured environment, it is possible to use the 'packages.txt' file for installation, with the command:
```
pip install -r packages.txt
```

### :rocket: Usage

All the input information for executing the tool should be passed into the input file, in the json format, which it must be in the 'processing/inputs' directory. After, for running the application, the 'main.py' file with the correct arguments must be executed.

The 'main.py' file has two arguments, the first is required and the second no:
```
python main.py -f [--file] <input filename> -o [--output] <directory of the output>
```

When startting the tool, it will run all the iteration steps until convergence is achieved. All the output files will be stored in the 'processing/outputs' directory with the properlly filename.

The input file has a schema that should be followed:
```
{
    "optimization": {
        "quantityOfParticles": 5,
        "maximumIterations": 10,
        "tolerance": 0.0001,
        "constantHyperParameters": false,
        "xfoilInstances": 10
    },
    "flightConditions": {
        "speed": 20.0,
        "viscosity": 1.789e-5,
        "temperature": 288.2,
        "airDensity": 1.225,
        "engineSpin": 1000
    },
    "propellerGeometricConditions": {
        "airfoil": "clarckY",
        "bladeDiameter": 2.4384,
        "numberOfBlades": 2,
        "AoAInMaximumEfficiency": 5.0,
        "radius": [
            0.254,
            0.3048,
            0.4572,
            0.6096,
            0.762,
            0.9144,
            1.0668,
            1.2192
        ],
        "chord": [
            0.122428,
            0.139192,
            0.174244,
            0.185166,
            0.179324,
            0.16129,
            0.128524,
            0
        ]
    },
    "airfoilGeometry": {
        "xPoints": [
            1.000000,
            0.331319,
            0.000270,
            0.329398,
            1.000000
        ],
        "yPoints": [
            0.000000,
            0.079169,
            0.001311,
           -0.021837,
            0.000000
        ]
    }
}
```

| Key | Description |
| --- | --- |
| quantityOfParticles | Represents the total number of particles in the optimization. |
| maximumIterations | Represents the maximum number of iteration steps in the optimization. |
| tolerance | Represents the minimum tolererance value for consedering a converged solution, and stop the iterative process. |
| constantHyperParameters | If 'true', indicates that the hyperparameters will always be constant along the iterative process, else will change them along the process. |
| xfoilInstances | Represents the maximum number of xfoil instances that will be used during the optimization process. Maximum number is 10. |
| flightConditions | Represents the flight condition which the propeller will be optimized. |
| speed | Aircraft speed (m/s). |
| viscodity | Air dynamic viscosity (Ns/m2). |
| temperature | Temperature of the air (K). |
| airDensity | Density of the air (kg/m3). |
| engineSpin | Engine spin (rpm) |
| propellerGeometricConditions | Represents the geometric conditions which should be followed during the optimization. |
| airfoil | Name of the airfoil. If naca foil, must follow like 'naca 0020'. |
| bladeDiameter | Diameter of the propeller (m) |
| numberOfBlades | Number os blades in the propeller |
| AoAInMaximumEfficiency | Angle of attack condition of the blade which will be executed the optimization. |
| radius | Distances from the center of the propeller, where the airfoil sections are located. Must only have 8 sections. |
| chord | Size of the section where the airfoils are located (m). Must only have 8 sections. |
| airfoilGeometry | Normalized bezier P points of an airfoil. If specified, will not consider the airfoil name, in case of naca foils. |

When the optimization process ends, the following outputs will be generated:

- Airfoils coordinates of the best solution, in txt files
- Illustration of the airfoils along the blade section
- Variables evolution along the iterative process
- Excel results per particle along the iterative process
- Efficiency x advance rate of the best particle
- Evolution of the objective function
- Torque x advance rate of the best particle
- Tracion x advance rate of the best particle

### :microscope: References

- `KENNEDY, J.; EBERHART, R. Particle swarm optimization. Proceedings of ICNN’95 - International Conference on Neural Networks, 1995`

- `CANAVER, G. S. Otimização de pás de hélice utilizando o algoritmo de otimização por enxame de partículas (PSO) e a teoria dos elementos de pá. Faculdade de Engenharia de São João da Boa Vista (UNESP), 2023.`