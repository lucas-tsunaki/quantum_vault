"""
This script implements a SWAP test for the verification of the quantum vault protocol,
as discussed in "Quantum Vault: Secure Token Authentication Without Classical Side Information Benchmarked on IBMQ"
by Lucas Tsunaki and Boris Naydenov, arXiv:2605.03564. 
"""

import numpy as np

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

service = QiskitRuntimeService(channel="ibm_quantum_platform",
                                    token="", # your token and instance go here
                                    instance="")

def qtvault_circuit_diff(
        theta1 : float,
        phi1 : float,
        theta2 : float,
        phi2 : float,
        N : int
):
    """
    Generates quantum vault circuit

    Parameters
    ----------
    theta1 : float
        Theta angle on Bloch shhere for first token state
    phi1 : float
        Phi angle on Bloch sphere for first token state
    theta2 : float
        Theta angle on Bloch shhere for second token state
    phi2 : float
        Phi angle on Bloch sphere for second token state
    N : int
        Number of swap-test rounds
    """

    circuit = QuantumCircuit(3, N)

    circuit.r(theta=theta1, phi=phi1, qubit=0)
    circuit.r(theta=theta2, phi=phi2, qubit=1)

    # repeats N times the measurement of the SWAP test
    for idx_N in range(N):
        circuit.barrier()
        circuit.reset(2)
        circuit.h(2)
        circuit.cswap(2, 0, 1)
        circuit.h(2)
        circuit.measure(2, idx_N)

    return circuit

real_backend = service.backend('ibm_marrakesh')

# light optmization without gate approximation and gate cancelation
pass_manager = generate_preset_pass_manager(optimization_level=0,
                                            backend=real_backend,
                                            layout_method='dense',
                                            translation_method="synthesis",
                                            approximation_degree=1)

# other parameters
sampler = SamplerV2(real_backend)
N=20
shots=1000

# input the desired angles here
theta1 = np.arccos(np.random.uniform(-1,1))
theta2 = np.arccos(np.random.uniform(-1,1))
phi1 = np.random.uniform(0,2*np.pi)
phi2 = np.random.uniform(0,2*np.pi)

# generates, transpiles and runs circuit
circuit = qtvault_circuit_diff(
    theta1,
    phi1,
    theta2,
    phi2,
    N
    )

transpiled_qc = pass_manager.run(circuit)
job = sampler.run(transpiled_qc, shots=shots)

print(job.job_id(), real_backend)