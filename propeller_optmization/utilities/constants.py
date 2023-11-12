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