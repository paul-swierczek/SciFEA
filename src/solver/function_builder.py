import numpy as np
import math
import sympy as sp

# ======================================== 
# Klasa konwersji dystrybucji obciążenia
# ======================================== EDYTOR OBCIĄŻEŃ + SOLVERY
class FormulateDistribution:
    def __init__(self, load_data, sym_dict = None, sympy_local = None):
        self.load_data = load_data
        self.type = self.load_data["type"]
        self.Ax_factor = self.load_data["axial_factor"]
        self.Norm_factor = self.load_data["normal_factor"]
        self.Base_intensity = self.load_data["base_intensity"]
        self.points = self.load_data["points"]
        self.num_of_points = self.load_data["n_points"]
        self.sym_dict = sym_dict
        self.sympyLOCAL = sympy_local

    # konwerotwanie wartości:
    def validate_val(self, val, sym_key, flag = False, return_raw = False):
        # Próba zamiana na float:
        try:
            abs_val = float(val)
            if flag:
                return abs_val, True
            return abs_val
        except Exception:
            if not self.sym_dict:
                if flag:
                    return val, False
                return val
            else:
                try:
                    sym_val = sp.sympify(val, locals = self.sympyLOCAL)
                    abs_val = sym_val.subs(self.sym_dict.get(sym_key, {}) | self.sym_dict.get("dimensionless", {}))
                    abs_val = float(abs_val)
                    if flag and return_raw:
                        return val, True
                    elif flag:
                        return abs_val, True
                    elif return_raw:
                        return val
                    else:
                        return abs_val
                except Exception:
                    if flag:
                        return val, False
                    return val
    
    # pomocnicz funkcja do generowania równania liniowego:
    def get_sp_linear_func(self, pt_1, pt_2):
        x_1 = pt_1[0]
        f_1 = pt_1[1]
        x_2 = pt_2[0]
        f_2 = pt_2[1]
        if sp.N(self.validate_val(val = x_1, sym_key = "dimensionless"), 9) == sp.N(self.validate_val(val = x_2, sym_key = "dimensionless"), 9):
            return False
        else:
            A = sp.simplify((f_2 - f_1)/(x_2 - x_1))
            B = sp.simplify(f_1 - A*x_1)
            return [A, B]

    # tworzenie bezwymiarowych funkcji:
    def SymPy_dimensionless(self, numerical = False):
        # tworzenie wyrażeń:
        xi_e = sp.Symbol("xi_e", real=True)
        dim_subs = self.sym_dict.get("dimensionless", {}) if self.sym_dict else {}

        def parse_exact(val):
            # Jeśli wartość jest floatem, zamieniamy ją na str,
            # aby sympify(..., rational=True) faktycznie zamieniło ją na ułamek dokładny
            if isinstance(val, float):
                val = str(val)
            return sp.sympify(val, locals = self.sympyLOCAL, rational = True)

        if self.type == "piecewise_linear":
            segments = []  # lista robocza elementów: [expr, t_start, t_end]

            # Sortujemy punkty rosnąco po t na wypadek wpisania ich w dowolnej kolejności
            sorted_points = sorted(
                self.points,
                key=lambda p: float(self.validate_val(p["t"], sym_key="dimensionless"))
            )

            for i in range(len(sorted_points) - 1):
                t_1 = parse_exact(sorted_points[i]["t"])
                val_1 = parse_exact(sorted_points[i]["val"])
                t_2 = parse_exact(sorted_points[i + 1]["t"])
                val_2 = parse_exact(sorted_points[i + 1]["val"])

                linear = self.get_sp_linear_func([t_1, val_1], [t_2, val_2])
                if not linear:
                    continue

                expr = sp.simplify(linear[0] * xi_e + linear[1])

                # Porównujemy rozwiniętą różnicę wyrażeń z poprzednim odcinkiem
                if segments and sp.simplify(sp.expand(expr - segments[-1][0])) == 0:
                    segments[-1][2] = t_2
                else:
                    segments.append([expr, t_1, t_2])

            pieceWise_list = []
            for idx, (expr, t_start, t_end) in enumerate(segments):
                if idx == len(segments) - 1:
                    cond = (t_start <= xi_e) & (xi_e <= t_end)
                else:
                    cond = (t_start <= xi_e) & (xi_e < t_end)
                pieceWise_list.append((expr, cond))

            pieceWise_list.append((0, True))
            pieceWise_func = sp.Piecewise(*pieceWise_list)

            if numerical and dim_subs:
                pieceWise_func = pieceWise_func.subs(dim_subs)
            return pieceWise_func
    
        elif self.type == "polynomial_bezier":
            # tworzenie listy:
            ctrl_vals = []
            for p_dict in self.points:
                ctrl_vals.append(sp.sympify(p_dict["val"], locals = self.sympyLOCAL))
            # Wielomian Bernsteina 5. stopnia na [0, 1]
            polynomial_bezier_expr = sum(
                ctrl_vals[i] * sp.binomial(self.num_of_points - 1, i) * xi_e**i * (1 - xi_e)**(self.num_of_points - 1 - i)
                for i in range(self.num_of_points)
            )
            polynomial_bezier_func = sp.expand(polynomial_bezier_expr)
            if numerical and dim_subs:
                polynomial_bezier_func = sp.expand(polynomial_bezier_func.subs(dim_subs))
            return polynomial_bezier_func

    # tworzenie razem z wymiarami:
    def SymPy_full(self, numerical = False):
        self.B_Ax = sp.sympify(f"({self.Ax_factor})*({self.Base_intensity})", locals = self.sympyLOCAL)
        self.B_Norm = sp.sympify(f"({self.Norm_factor})*({self.Base_intensity})", locals = self.sympyLOCAL)
        Base_distribution = self.SymPy_dimensionless(numerical = numerical)
        if numerical:
            self.B_AxNUM = self.validate_val(val = self.B_Ax, sym_key = "distributed_load")
            self.B_NormNUM = self.validate_val(val = self.B_Norm, sym_key = "distributed_load")
            base_ax = sp.simplify(self.B_AxNUM * Base_distribution)
            base_norm = sp.simplify(self.B_NormNUM * Base_distribution)
            return base_ax, base_norm
        base_ax = sp.simplify(self.B_Ax * Base_distribution)
        base_norm = sp.simplify(self.B_Norm * Base_distribution)
        return base_ax, base_norm

