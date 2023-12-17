INPUT_SCHEMA = {
    "optimization": {
        "quantityOfParticles": int,
        "maximumIterations": int,
        "tolerance": float,
        "constantHyperParameters": bool,
    },
    "flightConditions": {
        "speed": float,
        "viscosity": float,
        "tempeture": float,
        "airDensity": float,
        "bladeDiameter": float,
        "numberOfBlades": int,
        "engineSpin": int,
    },
    "propellerGeometricConditions": {
        "airfoil": str,
        "AoAInMaximumEfficiency": float,
        "radius": list,
        "chord": list,
    }
}

POINTS_BETWEEN_POINTS_P = 20

LIMITS_FOR_RANDOM_PROPELLER_SECTION_CHOOSE = {
    0: (-0.05, -0.036),
    1: (-0.035, -0.021),
    2: (-0.02, -0.006),
    3: (-0.005, 0.009),
    4: (0.01, 0.024),
    5: (0.025, 0.039),
    6: (0.04, 0.05),
}
