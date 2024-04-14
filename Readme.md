# **Propeller Optimization Tool** :airplane:

## *What is it?*

This tool was developed for optimizing the propulsion efficiency of aeronautical propellers. Aeronautical propellers are used as the main form of propulsion in many types of aircrafts, for over than 70 years. Propellers with high propulsion efficiency can reduce the emissions of $CO_2$ in the cruize flight.

For optimizing the propulsion efficiency, this application needs an input description of the propeller, such as the initial airfoil used, the flight condition, and the quantity of blades. After taking these informations, the application tries to modify the airfoils presented along each blade section, in an iterative process, aiming to obtain a propeller with better propulsion efficiency.

## *Table of contents*

- [Theorical background](#blue_book-theorical-background)

- [Architecture and tools](#hammer-architecture-and-tools)

- [Installation](#dvd-installation)

- [Usage](#rocket-usage)

- [References](#microscope-references)

### :blue_book: Theorical background

#### **1. Optimization problem**

Any optimization problem tries to obtain the best solution for a given objective. This objective is always a function, dependent of the problem variables, and which can be maximized or minimized; in other words, this function is called the objective function.

In the most optimization problems, the variables have certain limits of values, since a combination of variables could lead to an impractible solution for the problem. For limiting these values, new expressions are proposed, called constraints.

A nice introduction to optimization can be found in the following article from medium [``Optimization introduction``](https://medium.com/insiderfinance/optimization-for-beginners-optimization-for-beginners-a-guide-to-solving-optimization-problems-ae2192f9b15d)

#### **2. Particle Swarm Optimization (PSO)**

This optimization algorithm is based on the idea of existence of intelligence in bird migrations, which can be decomposed in a global intelligence (the intelligence of all birds together) and a local intelligence (the intelligence of each individual bird), all of them together for successful movements. Each bird in the algorithm is called a particle, which represents a possible solution for the problem, with its particular variables and objective value. This algorithm was choosen as the optimizer; it was choosen due to its non-linearity convergence, which is the type of problem when working with airfoils and propellers.

The iteration process begin with some starting variables, which are updated according to the algorithm proceeds, as ilustrated in the following equation:

$$X_{k+1}=X_k + V_{k+1} \cdot \Delta t$$

where $X_k$ is the variables in the $k$ iteration step, $V_k$ is the velocity associated to the movements, and $\Delta t$ is the step difference per iteration. The next velocity term can be calculated as:

$$V_{k+1}=\omega V_k + c_1 r_1 \frac{p_{best} - X_k}{\Delta t} + c_2 r_2 \frac{g_{best} - X_k}{\Delta t}$$

where $c_1$, $c_2$, $r_1$ and $r_2$ are hypermarameters associated; $p_{best}$ is the best particle variables for each particle, and $g_{best}$ is the best particle variables of all particles.

Better understanding of the algorithm can be found in the Kennedy and Eberhart original article: ``KENNEDY, J.; EBERHART, R. Particle swarm optimization. Proceedings of ICNN’95 - International Conference on Neural Networks, 1995``.

#### **3. Optimization variables and objective function**

The objective function of this tool is to maximize the propulsion efficiency. According to El-Sayed, 2017, the propulsion efficiency can be obtained in terms of the traction ($C_T$) and torque ($C_q$) coefficients, and the advance rate ($J$) of the propeller, thus, it can be written as:

$$F.O = max (J \frac{C_T}{C_q})$$

Futhermore, the optimization variables, $C_T$ and $C_q$, depends to the infinity airfoils shape along the blade. As it is almost impossible to consider the contribution of all airfoil sections, thus, for calculating the optimization variables along the iteration process, was utilized The Blade Element Theory, which discretizes the blade in some airfoil sections, and contributes in lift and drag for the blade.

Changing these airfoils shape results in different propellers, or different possibilities of solutions. So, for modifying the shapes, the conception of a Bezier Curve was used; in a nutshell, it takes the spline of the airfoil and obtain some points (A, B and P points), which can be easily changed for creating a new geometry. Thus, a movement value in a specific point of A was utilized as the main variables in the optimiztion variables, which changes the aerodynamic caracteristics of the airfoil, and for consequence, changes $C_T$ and $C_q$ coefficients.

Better understanding of the Bezier Curves and The Blade Element Theory can be found in the next links:

- [``Bézier Curve``](https://omaraflak.medium.com/b%C3%A9zier-curve-bfffdadea212)

- [``The Blade Element Theory``](https://www.aerodynamics4students.com/propulsion/blade-element-propeller-theory.php)

### :hammer: Architecture and tools

### :dvd: Installation

### :rocket: Usage

### :microscope: References