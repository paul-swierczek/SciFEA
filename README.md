# SciFEA
Hybrid symbolic-numeric 2D Finite Element Analysis (FEA) environment for 1D structural elements in Python. Features a PySide6/Matplotlib pre-processor, 14 beam/frame/truss formulations (Euler-Bernoulli, Timoshenko, higher-order curvature DOFs), and controlled CAS solving via SymPy &amp; NumPy.
# SciFEA — Hybrid Symbolic-Numeric 2D FEA Environment

**SciFEA** is a desktop Finite Element Analysis (FEA) environment written in Python for static analysis of planar 1D structural systems (beams, frames, trusses, and springs). 

Unlike commercial black-box solvers that operate exclusively on floating-point numbers, SciFEA combines a numerical solver (**NumPy**) with a Computer Algebra System (**SymPy**), allowing users to retain geometric and material parameters as algebraic symbols throughout the stiffness matrix assembly and solution process.

> **Project Status:** Active development (B.Sc. Engineering Thesis at Warsaw University of Technology, Faculty of Power and Aeronautical Engineering — MEiL). The geometric pre-processor, data validation engine, and visualization canvas are complete; numerical and symbolic solver modules are currently being integrated.

---

## Key Features

### 1. Controlled Degree of Symbolicity (Hybrid Mode)
Purely symbolic FEA quickly suffers from expression swell as the number of degrees of freedom grows. SciFEA solves this by introducing selective symbol substitution:
* **Pure Numerical Mode:** Fast floating-point execution via NumPy.
* **Pure Symbolic Mode:** Closed-form analytical stiffness matrices and nodal displacement equations via SymPy.
* **Hybrid Mode:** Keep only key design variables (e.g., cross-section height or spring stiffness $k$) in symbolic form while evaluating the rest numerically.

### 2. Finite Element Library (14 Formulations)
SciFEA supports two structural topologies (`Generalized_Coordinate_Framing` for arbitrary 2D frames/trusses and `Parallel_Beam_Approach` for orthogonal beam-rod systems) with 7 two-node element formulations each:
* **Euler-Bernoulli Beams / Frames:** Classical 2-node formulations (`2N4DOF_EB`, `2N6DOF_EB`).
* **Higher-Order Curvature Elements:** Beams and frames with nodal curvature ($\kappa = d^2w/dx^2$) as an additional degree of freedom (`2N6DOF_EB_Q`, `2N8DOF_EB_Q`).
* **Timoshenko-Reissner Beams / Frames:**
  * Exact analytical shear formulation (`TEX`)
  * Full Integration — 2-point Gauss quadrature (`T_FI`)
  * Reduced Integration — 1-point Gauss quadrature to prevent shear locking (`T_RI`)
* **Axial & Elastic Elements:** 1D/2D bars, trusses, and springs.

### 3. Data-Driven Pre-Processor & Visualization
* **Cross-Section Manager:** Automatic calculation of area ($A$), moment of inertia ($I_y$), extreme fiber distance ($z_{\max}$), and Żurawski's static moment for shear ($S$) across 11 parametric section shapes (I-beam, U-channel, T-beam, rectangular/circular tubes, etc.) with live Matplotlib contour preview.
* **Custom CAS Symbol Parser:** Safe expression parsing with automatic namespace isolation for engineering symbols (`E`, `I`, `S`) that otherwise collide with SymPy built-ins (Euler's number, imaginary unit, singleton registry).
* **Two-Tier Model Validation:** Real-time fault-tolerant rendering (highlighting corrupted nodes/elements on canvas instead of crashing) paired with a full pre-solver topological and mathematical validator.

---

## Architecture & Data Flow

The environment decouples the GUI pre-processor from the computational engines using structured, human-readable JSON files:

```text
[ Mesh Editor (PySide6) ] ──▶ *_msh.json  (Geometry, BCs, Materials, Sections, Symbols)
[ Load Editor (PySide6) ] ──▶ *_Lmsh.json (Nodal & distributed element loads)
                                   │
                                   ▼
                     [ Numeric / Symbolic Solvers ]
                                   │
                                   ▼
[ Post-Processor ]        ◀── *_Rmsh.json (Displacements, reactions, internal forces, LaTeX matrices)
