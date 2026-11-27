import numpy as np
import math
import sympy as sp

# ======================================== 
# Klasa konwersji dystrybucji obciążenia
# ======================================== EDYTOR OBCIĄŻEŃ + SOLVERY
class FormulateDistribution:
    """
    Klasa tworząca wielomiany beziera lub piecewise w sympy / numpy
    """
    def __init__(self, load_data: dict = None, sym_dict: dict = None, sympy_local: dict = None):
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
    def validate_val(self, val, sym_key: str, flag: bool = False, return_raw: bool = False):
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
    def get_sp_linear_func(self, pt_1: list, pt_2: list):
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
    def SymPy_dimensionless(self, numerical: bool = False):
        """
        Tworzy bezwymiarową (współrzędne naturalne) funkcję Sympy rozkładu obciążeń
        """
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
    def SymPy_full(self, numerical: bool = False):
        """
        tworzy funkcję pomnożoną o wpływ wektora kierunku działania obciążenia
        """
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


# ======================================== 
# Klasa dla wielokąta obciążeń regionalnych
# ======================================== EDYTOR OBCIĄŻEŃ
class PolygonContainmentChecker:
    """
    Klasa geometryczna operująca wyłącznie na listach wartości float.
    Obsługuje walidację wielokąta (brak samoprzecięć) - [is_valid_polygon] oraz ścisłą przynależność
    punktów i odcinków 1D  - [is_strictly_inside] (z wykluczeniem krawędzi i problemu wklęsłości).
    """
    def __init__(self, vertices: list[list[float]], eps: float = 1e-9):
        self.vertices = vertices
        self.num_vertices = len(vertices)
        self.eps = eps

    def _orientation(self, ax: float, az: float, bx: float, bz: float, cx: float, cz: float) -> int:
        # Iloczyn wektorowy (B - A) x (C - A)
        # 0 -> współliniowe, 1 -> przeciwnie do wskazówek zegara, 2 -> zgodnie ze wskazówkami
        val = (bx - ax) * (cz - az) - (bz - az) * (cx - ax)
        if abs(val) <= self.eps:
            return 0
        return 1 if val > 0.0 else 2

    def _on_bounding_box(self, px: float, pz: float, ax: float, az: float, bx: float, bz: float) -> bool:
        return (min(ax, bx) - self.eps <= px <= max(ax, bx) + self.eps and
                min(az, bz) - self.eps <= pz <= max(az, bz) + self.eps)

    def _is_point_on_segment(self, px: float, pz: float, ax: float, az: float, bx: float, bz: float) -> bool:
        return (self._orientation(ax, az, bx, bz, px, pz) == 0 and
                self._on_bounding_box(px, pz, ax, az, bx, bz))

    def _segments_intersect(
        self,
        ax: float, az: float, bx: float, bz: float,
        cx: float, cz: float, dx: float, dz: float
    ) -> bool:
        o1 = self._orientation(ax, az, bx, bz, cx, cz)
        o2 = self._orientation(ax, az, bx, bz, dx, dz)
        o3 = self._orientation(cx, cz, dx, dz, ax, az)
        o4 = self._orientation(cx, cz, dx, dz, bx, bz)

        # Przypadek ogólny: końce leżą po przeciwnych stronach drugiego odcinka
        if o1 != o2 and o3 != o4:
            return True

        # Przypadki szczególne: punkty współliniowe leżące na drugim odcinku
        if o1 == 0 and self._on_bounding_box(cx, cz, ax, az, bx, bz):
            return True
        if o2 == 0 and self._on_bounding_box(dx, dz, ax, az, bx, bz):
            return True
        if o3 == 0 and self._on_bounding_box(ax, az, cx, cz, dx, dz):
            return True
        if o4 == 0 and self._on_bounding_box(bx, bz, cx, cz, dx, dz):
            return True

        return False

    def is_valid_polygon(self):
        """
        Zwraca: True/False, txt. Txt przechowuje informację o tym jaki jest problem w wielokącie
        """
        n = self.num_vertices
        if n < 3:
            return False, (
                "A polygon must consist of at least 3 vertices."
            )

        double_area = 0.0
        for i in range(n):
            ax, az = self.vertices[i]
            bx, bz = self.vertices[(i + 1) % n]

            if abs(bx - ax) <= self.eps and abs(bz - az) <= self.eps:
                return False, (
                    f"Duplicate consecutive vertices detected (vertex {i + 1} and {(i + 1) % n + 1} "
                    f"have identical coordinates). Remove the repeated point."
                )

            double_area += (ax * bz - bx * az)

        if abs(double_area) * 0.5 <= self.eps:
            return False, (
                "The specified points are collinear (the polygon area is 0). "
                "Vertices cannot lie on a single straight line."
            )

        for i in range(n):
            ax, az = self.vertices[i]
            bx, bz = self.vertices[(i + 1) % n]

            for j in range(i + 1, n):
                cx, cz = self.vertices[j]
                dx, dz = self.vertices[(j + 1) % n]

                # Adjacent edges
                if j == i + 1:
                    if (self._is_point_on_segment(ax, az, cx, cz, dx, dz) or
                            self._is_point_on_segment(dx, dz, ax, az, bx, bz)):
                        return False, (
                            f"Edges {i + 1}-{i + 2} and {j + 1}-{(j + 1) % n + 1} overlap "
                            f"(0° or 180° angle between adjacent sides). Correct the order or position of the points."
                        )
                elif i == 0 and j == n - 1:
                    if (self._is_point_on_segment(bx, bz, cx, cz, dx, dz) or
                            self._is_point_on_segment(cx, cz, ax, az, bx, bz)):
                        return False, (
                            f"Closing edge {n}–1 overlaps with the first edge 1–2. "
                            f"Correct the order or position of the vertices."
                        )
                else:
                    # Non-adjacent edges (e.g. bow-tie / figure-eight shape or vertex touching another edge)
                    if self._segments_intersect(ax, az, bx, bz, cx, cz, dx, dz):
                        return False, (
                            f"Polygon edges intersect or touch each other (edges {i + 1}-{i + 2} "
                            f"and {j + 1}-{(j + 1) % n + 1}). The polygon must be a simple region without self-intersections."
                        )

        return True, ""

    def is_strictly_inside(self, px: float, pz: float) -> bool:
        if self.num_vertices < 3:
            return False

        inside = False
        j = self.num_vertices - 1

        for i in range(self.num_vertices):
            ax, az = self.vertices[i]
            bx, bz = self.vertices[j]

            if self._is_point_on_segment(px, pz, ax, az, bx, bz):
                return False

            if (az > pz) != (bz > pz):
                intersect_x = ax + (pz - az) * (bx - ax) / (bz - az)
                if px < intersect_x:
                    inside = not inside

            j = i

        return inside

    def is_segment_strictly_inside(self, x1: float, z1: float, x2: float, z2: float) -> bool: 
        """
        Zwraca True tylko wtedy, gdy oba węzły leżą ściśle wewnątrz wielokąta,
        a cały odcinek nie przecina ani nie dotyka żadnej krawędzi wielokąta (problem 'litery U').
        """
        if not (self.is_strictly_inside(x1, z1) and self.is_strictly_inside(x2, z2)):
            return False

        for i in range(self.num_vertices):
            ax, az = self.vertices[i]
            bx, bz = self.vertices[(i + 1) % self.num_vertices]

            if self._segments_intersect(x1, z1, x2, z2, ax, az, bx, bz):
                return False

        return True


# ======================================== 
# Funkcje pomocnicze, zrobione by nie zaśmiecać kodu
# ========================================
class LinearDistribution:
    """
    funkcja rozkładu liniowego
    """
    def __init__(self, pt_1:list, pt_2: list):
        self.pt_1 = pt_1
        self.pt_2 = pt_2

    def solve(self, x:float) -> float:
        x_1 = self.pt_1[0]
        f_1 = self.pt_1[1]
        x_2 = self.pt_2[0]
        f_2 = self.pt_2[1]
        A = (f_2 - f_1)/(x_2 - x_1)
        B = (f_1 - A*x_1)
        return A * x + B

class CosinusoidalDistribution:
    """
    funkcja rozkładu cosinusa
    """
    def __init__(self, pt_1:list, pt_2: list):
        self.pt_1 = pt_1
        self.pt_2 = pt_2

    def solve(self, x:float) -> float:
        """
        działa tylko kiedy: x_2 > x_1, z_1 > z_2 oraz x_1 < x < x_2
        """
        x_1 = self.pt_1[0]
        z_1 = self.pt_1[1]
        x_2 = self.pt_2[0]
        z_2 = self.pt_2[1]
        gap = z_1 - z_2
        span = x_2 - x_1
        t = (x - x_1) / span
        x_rad = t * (np.pi / 2)
        return z_2 + np.cos(x_rad) * gap

class HyperbolicDistribution:
    """
    Funkcja rozkładu hiperbolicznego (znormalizowana do przedziału [pt_1, pt_2]).
    Parametr `steepness` (k > 0) kontroluje stromość spadku (domyślnie 5.0).
    """
    def __init__(self, pt_1: list, pt_2: list, steepness: float = 5.0):
        self.pt_1 = pt_1
        self.pt_2 = pt_2
        self.steepness = steepness

    def solve(self, x: float) -> float:
        """
        Działa poprawnie dla x_2 != x_1 oraz x_1 <= x <= x_2.
        """
        x_1 = self.pt_1[0]
        z_1 = self.pt_1[1]
        x_2 = self.pt_2[0]
        z_2 = self.pt_2[1]

        gap = z_1 - z_2
        span = x_2 - x_1
        t = (x - x_1) / span  # normalizacja do [0, 1]

        # Znormalizowany spadek hiperboliczny z 1 (dla t=0) do 0 (dla t=1)
        k = self.steepness
        factor = (1.0 / (1.0 + k * t) - 1.0 / (1.0 + k)) / (1.0 - 1.0 / (1.0 + k))

        return z_2 + factor * gap

class ElementLoadFactorCalculator:
    """
    Niezależna klasa obliczająca lokalne współczynniki obciążenia (ax_factor, norm_factor)
    z uwzględnieniem rozkładu projection_factor dla trybu numerycznego i symbolicznego.
    Nie przyjmuje self.canvas.
    """
    def __init__(
        self,
        projection_func: str,
        projection_factor: float,
        is_symbolic: bool,
        eps: float = 1e-9
    ):
        self.projection_factor = float(projection_factor)
        self.is_symbolic = is_symbolic
        self.eps = eps
        self.distribution = self._create_distribution(projection_func)

    def _create_distribution(self, projection_func: str):
        p_start = [0.0, 1.0]
        p_end = [np.pi / 2.0, self.projection_factor]

        if projection_func == "linear":
            return LinearDistribution(p_start, p_end)
        elif projection_func == "cosinusoidal":
            return CosinusoidalDistribution(p_start, p_end)
        elif projection_func == "hyperbolic":
            return HyperbolicDistribution(p_start, p_end)
        else:
            raise ValueError(f"Unsupported projection_func: {projection_func}")

    def _compute_normal_deviations(self, theta: float) -> tuple[float, float]:
        """
        Zwraca kąty odchylenia osi globalnych X i Z od osi normalnej elementu
        w przedziale [0, pi/2].
        Układ: X - oś pozioma (0), Z - oś pionowa (pi/2).
        """
        sin_val = float(np.clip(abs(np.sin(theta)), 0.0, 1.0))
        cos_val = float(np.clip(abs(np.cos(theta)), 0.0, 1.0))

        x_rad = float(np.arccos(sin_val))
        z_rad = float(np.arccos(cos_val))
        return x_rad, z_rad

    def _to_clean_sympy_angle(self, global_angle: float):
        """
        Konwertuje float theta (rad) do dokładnego wyrażenia sympy z kontrolą
        zachowania kierunku (znaku) względem wejściowego floata.
        """
        global_angle_deg = np.degrees(global_angle)
        angle_round = round(global_angle_deg, 6)

        if (global_angle > 0.0 and angle_round < 0.0) or (global_angle < 0.0 and angle_round > 0.0):
            angle_round = -angle_round

        if abs(abs(angle_round) - 180.0) <= self.eps:
            angle_round = -180.0 if global_angle < 0.0 else 180.0

        angle_sym = sp.Rational(str(angle_round))
        return angle_sym / 180 * sp.pi

    def _to_clean_sympy_factor(self, value: float):
        """Zamienia wynik float z .solve() na czystą liczbę wymierną lub całkowitą dla sympy."""
        if abs(value) <= self.eps:
            return sp.Integer(0)
        if abs(value - 1.0) <= self.eps:
            return sp.Integer(1)
        return sp.Rational(str(round(value, 6)))

    def compute_for_element(
        self,
        theta: float,
        x_factor_float: float,
        z_factor_float: float,
        x_fac_line,
        z_fac_line
    ) -> tuple:
        """
        Zwraca (ax_factor, norm_factor) jako:
        - (float, float) w trybie numerycznym,
        - (str, str) w trybie symbolicznym.
        Zakłada, że x_fac_line oraz z_fac_line zawierają już właściwy znak.
        """
        # 1. Kąty odchylenia od osi normalnej (zawsze w [0, pi/2])
        x_rad, z_rad = self._compute_normal_deviations(theta)

        # 2. Współczynniki redukcji (projekcji) z rozkładu
        proj_x = float(self.distribution.solve(x_rad))
        proj_z = float(self.distribution.solve(z_rad))

        if not self.is_symbolic:
            # --- TRYB NUMERYCZNY ---
            qx_eff = float(x_fac_line) * proj_x
            qz_eff = float(z_fac_line) * proj_z

            cos_t = float(np.cos(theta))
            sin_t = float(np.sin(theta))

            ax_factor = qx_eff * cos_t + qz_eff * sin_t
            norm_factor = -qx_eff * sin_t + qz_eff * cos_t

            if abs(ax_factor) <= self.eps:
                ax_factor = 0.0
            if abs(norm_factor) <= self.eps:
                norm_factor = 0.0

            return ax_factor, norm_factor

        # --- TRYB SYMBOLICZNY ---
        angle_rad = self._to_clean_sympy_angle(theta)
        cos_sym = sp.cos(angle_rad)
        sin_sym = sp.sin(angle_rad)

        proj_x_sym = self._to_clean_sympy_factor(proj_x)
        proj_z_sym = self._to_clean_sympy_factor(proj_z)

        # x_fac_line i z_fac_line mają już własny znak (np. "-1/2"), więc nie negujemy ich ponownie
        qx_sym = sp.Integer(0) if abs(x_factor_float) <= self.eps else sp.sympify(x_fac_line)
        qz_sym = sp.Integer(0) if abs(z_factor_float) <= self.eps else sp.sympify(z_fac_line)

        qx_eff_sym = qx_sym * proj_x_sym
        qz_eff_sym = qz_sym * proj_z_sym

        ax_expr = sp.simplify(qx_eff_sym * cos_sym + qz_eff_sym * sin_sym)
        norm_expr = sp.simplify(-qx_eff_sym * sin_sym + qz_eff_sym * cos_sym)

        return str(ax_expr), str(norm_expr)

class PolygonArrowHatcher:
    def __init__(self, polygon_points: dict[str, list[float]]):
        # Sortowanie po kluczu numerycznym gwarantuje poprawną kolejność wierzchołków
        sorted_keys = sorted(polygon_points.keys(), key=lambda k: int(k))
        self.vertices = [polygon_points[k] for k in sorted_keys]

    def get_arrows(self, theta: float, num_lines: int = 20) -> list[tuple[list[float], list[float]]]:
        """
        Zwraca listę par punktów [(pt_1, pt_2), ...] dla strzałek kreskujących wielokąt
        pod kątem theta (w radianach).
        """
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        # 1. Obrót wierzchołków do lokalnego układu (u, v), gdzie oś u to kierunek strzałki
        rotated = [
            (x * cos_t + z * sin_t, -x * sin_t + z * cos_t)
            for x, z in self.vertices
        ]

        v_coords = [v for _, v in rotated]
        v_min, v_max = min(v_coords), max(v_coords)

        if v_max == v_min:
            return []

        # 2. Wyznaczenie poziomów linii skanujących z zachowaniem marginesu na brzegach
        step = (v_max - v_min) / num_lines
        scanlines = [v_min + (i + 0.5) * step for i in range(num_lines)]

        n = len(rotated)
        arrows = []

        # 3. Szukanie przecięć każdej linii skanującej z krawędziami wielokąta
        for v_k in scanlines:
            intersections_u = []

            for i in range(n):
                u1, v1 = rotated[i]
                u2, v2 = rotated[(i + 1) % n]

                # Reguła przedziału półotwartego poprawnie obsługuje wierzchołki leżące na linii
                # oraz automatycznie pomija krawędzie poziome (v1 == v2)
                if (v1 <= v_k < v2) or (v2 <= v_k < v1):
                    t = (v_k - v1) / (v2 - v1)
                    u_inter = u1 + t * (u2 - u1)
                    intersections_u.append(u_inter)

            intersections_u.sort()

            # 4. Łączenie przecięć w pary (dla kształtu U jedna linia da 2 oddzielne strzałki)
            for j in range(0, len(intersections_u) - 1, 2):
                u_start = intersections_u[j]
                u_end = intersections_u[j + 1]

                if u_end - u_start < 1e-9:
                    continue

                # 5. Obrót powrotny do oryginalnego układu (x, z)
                pt_1 = [
                    u_start * cos_t - v_k * sin_t,
                    u_start * sin_t + v_k * cos_t,
                ]
                pt_2 = [
                    u_end * cos_t - v_k * sin_t,
                    u_end * sin_t + v_k * cos_t,
                ]
                arrows.append((pt_1, pt_2))

        return arrows
