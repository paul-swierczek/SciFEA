import sympy as sp
import os
import json
import math

# Aktywacja ładnego wyświetlania
sp.init_printing()

# ==========================================
# STREFA 1: SZABLONY (KLASY)
# ==========================================

# Definicje materiałów
class material:
    def __init__(self, name, E, density):
        self.name = name
        self.E = E
        self.density = density

steel = material("steel", sp.symbols('E_s'), sp.symbols('rho_s'))
concrete = material("concrete", sp.symbols('E_c'), sp.symbols('rho_c'))
wood = material("spruce_wood", sp.symbols('E_w'), sp.symbols('rho_w'))
material_library=[steel, concrete, wood]
# ====================
# Definicje węzłów
# ====================
class node:
    def __init__(self, node_id, constraint):
        self.id = node_id
        self.constraint = constraint
        self.n_dof = 0
        self.dof = []
        self.dof_type = []
# ====================
# Definicje elementów
# ====================
# Nieznany element
class Unknown_element:
    def __init__(self, id, node_a, node_b, material, Area_val, Area_symbol, length_val, length_symbol, I_val, I_symbol):
        self.id = id
        self.type = "Unknown_element"
        self.n1 = node_a
        self.n2 = node_b
        self.mat = material
        self.Area_val = Area_val
        self.Area_Sym = Area_symbol
        self.length_val = length_val
        self.length_Sym = length_symbol
        self.I_val = I_val
        self.I_Sym = I_symbol
    def A(self):
        Symbol = sp.symbols(f'{self.Area_Sym}')
        Value = sp.sympify(self.Area_val)
        return Value * Symbol
    def L(self):
        Symbol = sp.symbols(f'{self.length_Sym}')
        Value = sp.sympify(self.length_val)
        return Value * Symbol
    def I(self):
        Symbol = sp.symbols(f'{self.I_Sym}')
        Value = sp.sympify(self.I_val)
        return Value * Symbol    
    def Stiff_M(self):
        scalar = sp.symbols('?')
        base_matrix = sp.Matrix([[scalar, scalar], [scalar, scalar]])
        return base_matrix
# Sprężyna 1D
class El_Spring:
    def __init__(self, id, node_a, node_b, material, stiffness_val, stiffness_symbol):
        self.id = id
        self.type = "Spring"
        self.n1 = node_a
        self.n2 = node_b
        self.mat = material
        self.stif_val = stiffness_val
        self.stif_Sym = stiffness_symbol 
        self.dof = []
    def k(self):
        Symbol = sp.sympify(f'{self.stif_Sym}')
        Value = sp.sympify(self.stif_val)
        return Value * Symbol
    def Stiff_M(self):
        scalar = self.k()
        base_matrix = sp.Matrix([[1, -1], [-1, 1]])
        return sp.MatMul(scalar, base_matrix, evaluate = False)
# Pręt 1D
class El_2N2DOF:
    def __init__(self, id, node_a, node_b, material, Area_val, Area_symbol, length_val, length_symbol):
        self.id = id
        self.type = "2N2DOF"
        self.n1 = node_a
        self.n2 = node_b
        self.mat = material
        self.Area_val = Area_val
        self.Area_Sym = Area_symbol
        self.length_val = length_val
        self.length_Sym = length_symbol
        self.dof = []
    def A(self):
        Symbol = sp.symbols(f'{self.Area_Sym}')
        Value = sp.sympify(self.Area_val)
        return Value * Symbol
    def L(self):
        Symbol = sp.symbols(f'{self.length_Sym}')
        Value = sp.sympify(self.length_val)
        return Value * Symbol   
    def Stiff_M(self):
        scalar = self.mat.E * self.A() / self.L()
        base_matrix = sp.Matrix([[1, -1], [-1, 1]])
        return sp.MatMul(scalar, base_matrix, evaluate = False)
# Belka 1D Eulera
class El_2N4DOF:
    def __init__(self, id, node_a, node_b, material, Area_val, Area_symbol, length_val, length_symbol, I_val, I_symbol):
        self.id = id
        self.type = "2N4DOF_EB"
        self.n1 = node_a
        self.n2 = node_b
        self.mat = material
        self.Area_val = Area_val
        self.Area_Sym = Area_symbol
        self.length_val = length_val
        self.length_Sym = length_symbol
        self.I_val = I_val
        self.I_Sym = I_symbol
        self.dof = []
    def A(self):
        Symbol = sp.symbols(f'{self.Area_Sym}')
        Value = sp.sympify(self.Area_val)
        return Value * Symbol
    def L(self):
        Symbol = sp.symbols(f'{self.length_Sym}')
        Value = sp.sympify(self.length_val)
        return Value * Symbol
    def I(self):
        Symbol = sp.symbols(f'{self.I_Sym}')
        Value = sp.sympify(self.I_val)
        return Value * Symbol  
    def Stiff_M(self):
        scalar = 2 * self.mat.E * self.I() / self.L()**3
        base_matrix = sp.Matrix([[6, 3*self.L(), -6, 3*self.L()], [3*self.L(), 2*self.L()**2, -3*self.L(), self.L()**2], [-6, -3*self.L(), 6, -3*self.L()], [3*self.L(), self.L()**2, -3*self.L(), 2*self.L()**2]])
        return sp.MatMul(scalar, base_matrix, evaluate = False)
# Pręt 2D:
class El_2N2DOF_2D:
    def __init__(self, id, node_a, node_b, material, Area_val, Area_symbol, length_val, length_symbol, angle_val, angle_symbol):
        self.id = id
        self.type = "2N2DOF_2D"
        self.n1 = node_a
        self.n2 = node_b
        self.mat = material
        self.Area_val = Area_val
        self.Area_Sym = Area_symbol
        self.length_val = length_val
        self.length_Sym = length_symbol
        self.angle_val = angle_val
        self.angle_Sym = angle_symbol
        self.dof = []
    def A(self):
        Symbol = sp.symbols(f'{self.Area_Sym}')
        Value = sp.sympify(self.Area_val)
        return Value * Symbol
    def L(self):
        Symbol = sp.symbols(f'{self.length_Sym}')
        Value = sp.sympify(self.length_val)
        return Value * Symbol
    def Ang(self):
        Symbol = sp.symbols(f'{self.angle_Sym}')
        Value = sp.sympify(self.angle_val)
        return Value * Symbol
    def Stiff_M(self):
        scalar = self.mat.E * self.A() / self.L()
        c = sp.cos(self.Ang())
        s = sp.sin(self.Ang())
        base_matrix = sp.Matrix([[c**2, c*s, -c**2, -c*s], [c*s, s**2, -c*s, -s**2], [-c**2, -c*s, c**2, c*s], [-c*s, -s**2, c*s, s**2]])
        return sp.MatMul(scalar, base_matrix, evaluate = False)
# Sprężyna 2D
class El_Spring_2D:
    def __init__(self, id, node_a, node_b, material, stiffness_val, stiffness_symbol, angle_val, angle_symbol):
        self.id = id
        self.type = "Spring_2D"
        self.n1 = node_a
        self.n2 = node_b
        self.mat = material
        self.stif_val = stiffness_val
        self.stif_Sym = stiffness_symbol 
        self.angle_val = angle_val
        self.angle_Sym = angle_symbol
        self.dof = []
    def k(self):
        # Dano sp.sympify do sztywności k ale jest to ryzykowny, sp.sympify dla E dla liczbę eulera dlatego trzeba być ostrożnym dla I da pierwiastek z -1
        Symbol = sp.sympify(f'{self.stif_Sym}')
        Value = sp.sympify(self.stif_val)
        return Value * Symbol
    def Ang(self):
        Symbol = sp.symbols(f'{self.angle_Sym}')
        Value = sp.sympify(self.angle_val)
        return Value * Symbol
    def Stiff_M(self):
        scalar = self.k()
        c = sp.cos(self.Ang())
        s = sp.sin(self.Ang())
        base_matrix = sp.Matrix([[c**2, c*s, -c**2, -c*s], [c*s, s**2, -c*s, -s**2], [-c**2, -c*s, c**2, c*s], [-c*s, -s**2, c*s, s**2]])
        return sp.MatMul(scalar, base_matrix, evaluate = False)
# Rama 2D:
class El_2N6DOF_2DF:
    def __init__(self, id, node_a, node_b, material, Area_val, Area_symbol, length_val, length_symbol, I_val, I_symbol, angle_val, angle_symbol):
        self.id = id
        self.type = "2N6DOF_2DF"
        self.n1 = node_a
        self.n2 = node_b
        self.mat = material
        self.Area_val = Area_val
        self.Area_Sym = Area_symbol
        self.length_val = length_val
        self.length_Sym = length_symbol
        self.I_val = I_val
        self.I_Sym = I_symbol
        self.angle_val = angle_val
        self.angle_Sym = angle_symbol
        self.dof = []
    def A(self):
        Symbol = sp.symbols(f'{self.Area_Sym}')
        Value = sp.sympify(self.Area_val)
        return Value * Symbol
    def L(self):
        Symbol = sp.symbols(f'{self.length_Sym}')
        Value = sp.sympify(self.length_val)
        return Value * Symbol
    def Ang(self):
        Symbol = sp.symbols(f'{self.angle_Sym}')
        Value = sp.sympify(self.angle_val)
        return Value * Symbol
    def I(self):
        Symbol = sp.symbols(f'{self.I_Sym}')
        Value = sp.sympify(self.I_val)
        return Value * Symbol  
    def Stiff_M(self):
        c = sp.cos(self.Ang())
        s = sp.sin(self.Ang())
        l = self.L()
        # Skalary wyciągane przed macierz
        Db = 2 * self.mat.E * self.I() / l**3
        Dp = (self.mat.E * self.A() / l) / Db # Poprawny fizyczny stosunek sztywności
        base_matrix = sp.Matrix([
            [ Dp*c**2 + 6*s**2,      (Dp-6)*c*s,           -3*l*s,      -(Dp*c**2 + 6*s**2),     -(Dp-6)*c*s,          -3*l*s ],
            [ (Dp-6)*c*s,            Dp*s**2 + 6*c**2,      3*l*c,      -(Dp-6)*c*s,             -(Dp*s**2 + 6*c**2),   3*l*c ],
            [ -3*l*s,                3*l*c,                 2*l**2,      3*l*s,                  -3*l*c,                l**2  ],
            [ -(Dp*c**2 + 6*s**2),   -(Dp-6)*c*s,           3*l*s,       Dp*c**2 + 6*s**2,        (Dp-6)*c*s,           3*l*s ],
            [ -(Dp-6)*c*s,           -(Dp*s**2 + 6*c**2),  -3*l*c,       (Dp-6)*c*s,              Dp*s**2 + 6*c**2,    -3*l*c ],
            [ -3*l*s,                3*l*c,                 l**2,        3*l*s,                  -3*l*c,               2*l**2 ]
        ])   
        return sp.MatMul(Db, base_matrix, evaluate=False)
    
# ====================
# inne biblioteki
# ====================

# Ilość stopni swobody na element (w węźle):
dof_requirements = {
    "2N4DOF_EB": ["UZ", "RY"],
    "2N2DOF": ["UZ"],
    "Spring": ["UZ"],
    "2N2DOF_2D": ["UX", "UZ"],
    "Spring_2D": ["UX", "UZ"],
    "2N6DOF_2DF": ["UX", "UZ", "RY"]
}
# Słownik zawierający wartości symboli jakie wynikają z materiałów (użytkownik podaje materiał "steel" a program już wie jakie parametry ma stal)
Base_Symbol_substitute = {
    'E_s': 210e9,
    'E_c': 30e9,
    'E_w': 10e9
}
# Biblioteka jednostek:
Unit_substitute = {
    'N': {'value': 1.0, 'type': 'force', 'name': 'Newton', 'unit': sp.symbols(' N')},
    'kN': {'value': 0.001, 'type': 'force', 'name': 'kilo-Newton', 'unit': sp.symbols(' kN')},
    'Nm': {'value': 1.0, 'type': 'torque', 'name': 'Newton-Meter', 'unit': sp.symbols(' Nm')},
    'kNm': {'value': 0.001, 'type': 'torque', 'name': 'kilo-Newton-Meter', 'unit': sp.symbols(' kNm')},
    'm': {'value': 1.0, 'type': 'length', 'name': 'Meter', 'unit': sp.symbols(' m')},
    'cm': {'value': 100.0, 'type': 'length', 'name': 'Centimeter', 'unit': sp.symbols(' cm')},
    'mm': {'value': 1000.0, 'type': 'length', 'name': 'Milimeter', 'unit': sp.symbols(' mm')},
    'rad': {'value': 1.0, 'type': 'angle', 'name': 'Radian', 'unit': sp.symbols(' rad')},
    'deg': {'value': math.degrees(1.0), 'type': 'angle', 'name': 'arcdegree [°]', 'unit': sp.symbols('deg')}
}
# Typy siatek:
Mesh_types = {
    'Perpandicular_Beam_construction': {'supported elements': ["2N4DOF_EB", "2N2DOF", "Spring"]},
    'Truss_2D': {'supported elements': ["2N2DOF_2D", "Spring_2D"]},
    'Frame_2D': {'supported elements': ["2N2DOF_2D", "Spring_2D", "2N6DOF_2DF"]}
}
# Kolejność stopnii swobody:
DOF_ORDER = ["UX", "UY", "UZ", "RX", "RY", "RZ"]
# Lokalizacje folderów:
FOLDER_PATH = os.path.dirname(__file__)
FOLDER_PATH_LOAD = os.path.join(FOLDER_PATH, r"Loads")
# ==========================================
# STREFA 2: FUNKCJE (MODUŁY SOLVERA)
# ==========================================

# funkcja powitalna
def starting_solver():
    """Funkcja odpowiadająca wyłącznie za ładny start programu."""
    print("==================================================")
    print("       SYMBOLICZNY SOLVER MES - WERSJA MODUŁOWA   ")
    print("==================================================")
    


# ====================
# Funkcja wczytywania siatki:
# ====================
def mesh_load(folder_path):
    """Skanuje folder, pozwala wybrać plik i zwraca odczytany słownik JSON."""  
    try:
        all_components = os.listdir(folder_path) #odczyt całej zawartości folderu
        #tworzenie listy wszystkich plików tekstowych
        files_json = [i for i in all_components if i.endswith(".json") and os.path.isfile(os.path.join(folder_path, i))]
        #wyświetlanie wszystkich dostępnych plików
        if not files_json:
            print("No .json files found")
        else:
            print("Available .json files:")
            for i in files_json:
                print(f" - {i}")
        #błąd nie dostępu do ścieżki
    except OSError:
        print(f"cannot access files in {folder_path}")
    #wybór pliku:
    if files_json: 
        while True:
            selected_file = input("Select file (do not write .json): ")
            selected_path = os.path.join(folder_path, selected_file)
            if f"{selected_file}.json" in files_json:
                print(f"selected file: {selected_file} , location: {selected_path}")
                break
            else:
                print(f"{selected_file}.json not present in {folder_path}")
    # Otarcie pliku i zwrócenie danych
    with open(f"{selected_path}.json", 'r') as file:
        mesh_dat = json.load(file)
    return mesh_dat # Zwracamy "paczkę" z danymi z powrotem do głównego programu
# ====================
# Funkcja importu elementów i węzłów do solvera + wartości symboli
# ====================
def unpack_mesh(mesh_dat):
    """Zmienia surowy słownik na listy obiektów węzłów i elementów."""
    node_list = []
    element_list = []
    N_node = mesh_dat["model_summary"]["number of nodes"]
    N_element = mesh_dat["model_summary"]["number of elements"]
    # Tworzenie słowników symboli:
    mesh_subs_dict = mesh_dat["symbol_substitutes"]
    general_mesh_subs = {}
    angle_mesh_subs = {}
    for sym_name, sym_data in  mesh_subs_dict.items():
        # Kluczem słowników będzie sym_name
        val = sym_data.get("val", 0)
        value = sp.sympify(val)
        general_mesh_subs[sym_name] = value # Dodawanie klucza do słownika
        if sym_data["type"] == "angle":
            angle_mesh_subs[sym_name] = value # Dodatkowy słownik dla kąta
    # Używamy .get(), aby program nie wybuchł, jeśli ktoś zapomni dodać tego bloku w JSON
    mesh_type = mesh_dat.get("model_summary", {}).get("mesh_type", "Unknown")
    # 1. Wczytanie węzłów
    for n in range(N_node):
        read_node = node(mesh_dat["nodes"][n]["id"], mesh_dat["nodes"][n]["constraint"])
        node_list.append(read_node)  
    # 2. Wczytanie elementów
    for e in range(N_element):
        # Tworzymy krótką zmienną pomocniczą (alias) dla czytelności kodu
        el_data = mesh_dat["elements"][e] 
        el_type = el_data["type"]       
        if el_type == "2N2DOF":
            read_element = El_2N2DOF(
                el_data["id"], 
                el_data["node_1_id"], 
                el_data["node_2_id"], 
                el_data["material"], 
                el_data["Area_val"], 
                el_data["Area_symbol"], 
                el_data["length_val"], 
                el_data["length_symbol"])
        elif el_type == "2N4DOF_EB":
            read_element = El_2N4DOF(
                el_data["id"], 
                el_data["node_1_id"], 
                el_data["node_2_id"], 
                el_data["material"], 
                el_data["Area_val"], 
                el_data["Area_symbol"], 
                el_data["length_val"], 
                el_data["length_symbol"], 
                el_data["I_val"],  
                el_data["I_symbol"])
        elif el_type == "2N2DOF_2D":
            read_element = El_2N2DOF_2D(
                el_data["id"], 
                el_data["node_1_id"], 
                el_data["node_2_id"], 
                el_data["material"], 
                el_data["Area_val"], 
                el_data["Area_symbol"], 
                el_data["length_val"], 
                el_data["length_symbol"], 
                el_data["angle_val"],  
                el_data["angle_symbol"])
        elif el_type == "Spring":
            read_element = El_Spring(
                el_data["id"], 
                el_data["node_1_id"], 
                el_data["node_2_id"], 
                el_data["material"], 
                el_data["stiffness_val"], 
                el_data["stiffness_symbol"])
        elif el_type == "Spring_2D":
            read_element = El_Spring_2D(
                el_data["id"], 
                el_data["node_1_id"], 
                el_data["node_2_id"], 
                el_data["material"], 
                el_data["stiffness_val"], 
                el_data["stiffness_symbol"],
                el_data["angle_val"],  
                el_data["angle_symbol"])
        elif el_type == "2N6DOF_2DF":
            read_element = El_2N6DOF_2DF(
                el_data["id"], 
                el_data["node_1_id"], 
                el_data["node_2_id"], 
                el_data["material"], 
                el_data["Area_val"], 
                el_data["Area_symbol"], 
                el_data["length_val"], 
                el_data["length_symbol"], 
                el_data["I_val"],  
                el_data["I_symbol"],
                el_data["angle_val"],
                el_data["angle_symbol"])
        else:
            read_element = Unknown_element(
                el_data["id"], 
                el_data["node_1_id"], 
                el_data["node_2_id"], 
                el_data["material"], 
                el_data["Area_val"], 
                el_data["Area_symbol"], 
                el_data["length_val"], 
                el_data["length_symbol"], 
                el_data["I_val"],  
                el_data["I_symbol"])            
        element_list.append(read_element)  
    print(f"Data extracted: {N_node} nodes, {N_element} elements.")
    return node_list, element_list, mesh_type, general_mesh_subs, angle_mesh_subs
# ====================
# Funkcja sprawdzenia siatki i przypisania jej odpowiednich obiektów
# ====================
def check_mesh(nodes, elements, materials, mesh_type):
    """Sprawdza poprawność siatki i łączy ID ze wskaźnikami na obiekty."""
    mesh_valid = True
    properties_in_el_list = [] # Tylko w celu wyświetlenia w princie elementów (zadziała poprawnie, jeśli numeracja węzłów jest po kolei)
    for e in elements:
        n1_found = False
        n2_found = False  
        # 1. Sprawdzanie pierwszego węzła
        for n in nodes:
            if n.id == e.n1:
                e.n1 = n  # Podmiana ID na cały obiekt węzł
                e_n1 = n.id
                n1_found = True
                break
        if not n1_found:
            print(f"ERROR: Node ID {e.n1} (Node_A) not found. Element {e.id} is disconnected.")
            e.n1 = e_n1 = "NOT ASSIGNED"
            mesh_valid = False            
        # 2. Sprawdzanie drugiego węzła
        for n in nodes:
            if n.id == e.n2:
                e.n2 = n
                e_n2 = n.id
                n2_found = True
                break
        if not n2_found:
            print(f"ERROR: Node ID {e.n2} (Node_B) not found. Element {e.id} is disconnected.")
            e.n2 = e_n2 = "NOT ASSIGNED"
            mesh_valid = False  
        # Sprawdzenie, czy element nie łączy się sam ze sobą
        if n1_found and n2_found and e.n1.id == e.n2.id:
            print(f"ERROR: Element ID {e.id} is invalid. Node_A and Node_B are the same.")
            mesh_valid = False  
        # 3. Sprawdzanie materiału
        mat_found = False
        for mat in materials:
            if e.mat == mat.name:
                e.mat = mat
                e_mat = mat.name
                mat_found = True
                break
        if not mat_found:
            print(f"ERROR: Material '{e.mat}' not found for Element ID: {e.id}!")
            mesh_valid = False 
            e.mat = e_mat = "NOT ASSIGNED"
        properties_in_el_list.append([e_mat, e_n1, e_n2])
        if e.type == "Unknown_element":
            print(f"ERROR: Unknown element type not assigned for Element ID: {e.id}!")   
            mesh_valid = False
    # Sprawdzenie czy nie ma połączenia pręt 2D z belką:
    if mesh_type in Mesh_types:
        Supported = Mesh_types[mesh_type]["supported elements"]
        for e in elements:
            if e.type not in Supported:
                mesh_valid = False
                print(f"\nERROR: Element type {e.type} cannot be used in {mesh_type} mesh type")
                print(f"\n Viable {mesh_type} elements:")
                for name in Supported:
                    print(f" - {name}")
                break
    else:
        mesh_valid = False
        print(f"Mesh type {mesh_type} not present in library\n Supported mesh types:")
        for name in Mesh_types:
            print(f" - {name}")
    
    if mesh_valid:
        print("Mesh validation: OK!")
    else:
        print("Mesh validation: FAILED!")
    # Wyświetlenie listy elementów
    yn = input("Display elements? Y/N: ")
    if yn.lower() == "y":
        print("==== Imported Elements ====")
        for i, e in enumerate(elements):
            mat_name = properties_in_el_list[i][0]
            n1_id = properties_in_el_list[i][1]
            n2_id = properties_in_el_list[i][2]
            print(f"element_ID: {e.id} - {e.type} - {mat_name} connected nodes: {n1_id} -> {n2_id}")    
    return mesh_valid
# ====================
# Funkcja przypisania stopni swobody
# ====================
def assign_dofs(nodes, elements):
    # Faza 1: Zbieranie informacji, jakich typów DOF potrzebuje dany węzeł
    for n in nodes:
        wymagane_w_wezle = set()
        for e in elements:
            if e.n1.id == n.id or e.n2.id == n.id:
                wymagania_el = dof_requirements.get(e.type, [])
                wymagane_w_wezle.update(wymagania_el)
        
        # Zamiast: n.dof_type = sorted(list(wymagane_w_wezle))
        # Używamy sortowania z kluczem:
        n.dof_type = sorted(list(wymagane_w_wezle), key=lambda x: DOF_ORDER.index(x))
        n.n_dof = len(n.dof_type)

    # Faza 2: Nadawanie globalnych numerów DOF węzłom
    current_dof = 0
    for n in nodes:
        n.dof = [] # Dla bezpieczeństwa lista dof jest zerowana
        for t in n.dof_type:
            current_dof += 1
            n.dof.append(current_dof)

    # Faza 3: Elementy pobierają odpowiednie numery DOF z węzłów
    for e in elements:
        e.dof = [] # Dla bezpieczeństwa lista dof jest zerowana
        wymagania_el = dof_requirements.get(e.type, [])
        
        # Element iteruje po tym, czego sam wymaga i szuka tego w węźle 1
        for wymóg in wymagania_el:
            index_typu = e.n1.dof_type.index(wymóg) # np. na którym miejscu w n1 jest "displacement_Z"?
            e.dof.append(e.n1.dof[index_typu])      # pobierz odpowiadający mu numer globalny
            
        # To samo dla węzła 2
        for wymóg in wymagania_el:
            index_typu = e.n2.dof_type.index(wymóg)
            e.dof.append(e.n2.dof[index_typu])
    y_n = input("Display assigned element DOFs? Y/N: ")
    if y_n.lower() == "y":
        print("==== Imported DOFs ====")
        for e in elements:    
         print(f"Element_ID: {e.id}, DoF: {e.dof}")
    # Wymiar macierzy sztywności:
    M_dim = current_dof
    return M_dim
# ====================
# Funkcja tworząca listy stopni swobody
# ====================
def build_global_lists(nodes, M_dim):
    Glob_dof_id = [0] * M_dim
    Glob_dof_type = [0] * M_dim
    Glob_constraint = [0] * M_dim 
    
    for n in nodes:
        n_dof_local = len(n.dof)
        for i in range(n_dof_local):
            global_idx = n.dof[i] - 1
            dof_name = n.dof_type[i]
            Glob_dof_id[global_idx] = n.dof[i]
            Glob_dof_type[global_idx] = dof_name
            # Jeśli w JSON jest słownik, pobieramy wartość dla konkretnego typu.
            # Jeśli danego klucza nie ma (np. belka nie ma X), przyjmujemy domyślnie 0 (swobodny).
            Glob_constraint[global_idx] = n.constraint.get(dof_name, 0) # pobieranie 0 lub 1 dla słownika n.constraint
            
    return Glob_constraint, Glob_dof_type, Glob_dof_id
# ====================
# Funkcja czytająca plik obciążeń
# ====================
def assign_loads(load_folder_path, nodes, mesh_name, M_dim):
    try:
        all_components = os.listdir(load_folder_path) 
        files_json = [i for i in all_components if i.endswith("load.json") and os.path.isfile(os.path.join(load_folder_path, i))]
        
        if not files_json:
            print("No load.json files found")
            return None # Jeśli nie ma plików, bezpiecznie uciekamy z funkcji
        else:
            print("Available .json files:")
            for i in files_json:
                print(f" - {i}")
    except OSError:
        print(f"cannot access files in {load_folder_path}")
        return None

    if files_json: 
        while True:
            selected_file = input("Select file (do not write .json): ")

            selected_path = os.path.join(load_folder_path, selected_file)
            
            if f"{selected_file}.json" in files_json:
                print(f"selected file: {selected_file} , location: {selected_path}")
            else:
                print(f"{selected_file}.json not present in {load_folder_path}")
                continue # Wymusza powrót na początek pętli while
                
            try:
                with open(f"{selected_path}.json", 'r', encoding='utf-8') as file:
                    load_dat = json.load(file)
                    load_name = load_dat.get("model_summary", {}).get("mesh name")
                    # Tworzenie słownika z podstawieniami pod symbole obciążeń
                    load_sym_subs_dict = load_dat.get("symbol_substitutes", {})
                    load_sym_subs = {}
                    for sym_name, sym_data in load_sym_subs_dict.items():
                        val = sym_data.get("val", 0)
                        value = sp.sympify(val)
                        load_sym_subs[sym_name] = value

                    if load_name is None:
                        print("File does not contain 'model_summary.mesh name' key.")
                        continue    
                        
                    if load_name == mesh_name:
                        Glob_load = [0] * M_dim
                        for n in nodes:
                            # 1. Pobieramy cały słownik danego węzła z pliku JSON na podstawie jego ID
                            node_json = load_dat["nodes"][n.id - 1]["load"] 
                            
                            n_dof_local = len(n.dof)
                            for i in range(n_dof_local):
                                dof_name = n.dof_type[i] # Np. "UX"
                                # 2. Szukamy "UX" w słowniku tego konkretnego węzła. 
                                # Jeśli nie ma, dajemy pusty słownik {}
                                dof_data = node_json.get(dof_name, {}) 
                                symbol_name = dof_data.get("sym", 0)
                                # Zabezpieczenie "str(symbol_name)" przez wpisaniem int(0) do sp.symbols:
                                symbol = sp.symbols(str(symbol_name)) if symbol_name != 0 else 0 
                                value = dof_data.get("val", 0)
                                value = sp.sympify(value) # aby można było napisać po prostu "sqrt(2)" w value
                                # 3. Zapisujemy wynik do odpowiedniego wiersza w globalnym wektorze
                                # Tutaj n.dof[i] - 1 jest użyte prawidłowo!
                                Glob_load[n.dof[i] - 1] = value * symbol             
                            # Używamy return zamiast break, to od razu przerywa pętlę i zwraca wynik do Maina.
                        return Glob_load, load_sym_subs                
                    else:
                        print(f"File '{selected_file}' contains mesh '{load_name}', expected '{mesh_name}'. Please choose another file.")
            except Exception as e: 
                print(f"Error reading file {selected_file}.json: {e}")
                continue
# ====================
# Funkcja wyświetlania list stopni swobody, uwiązań i obciążeń
# ====================
def display_dof_lists(Glob_load, Glob_constraint, Glob_dof_type, Glob_dof_id):
    y_n = input("Display imported global DOFs? Y/N: ")
    if y_n.lower() == "y":
        print("==== Imported global DOFs ====")
        print(f"DOF IDs:\n{Glob_dof_id}")
        print(f"DOF type:\n{Glob_dof_type}")
        print(f"Constraints:\n{Glob_constraint}")
        print(f"Loads:\n{Glob_load}")
# ====================
# Funkcja tworząca globalną macierz sztywności oraz globalny wektor obciążeń:
# ====================
def aggregate_global(elements, M_dim, Glob_load):
    # Agregacja macierzy:
    K_global = sp.zeros(M_dim, M_dim)
    for e in elements:
        # wykrywanie wymiaru listy e.dof[] stopni swobody 2 lub 4 oraz lokalna macierz sztywności ( e.Stiff_M() ) będzie za każdym razem wyprowadzało macierz
        n_local= len(e.dof) 
        k_local = e.Stiff_M()
        for i in range(n_local):
            for j in range(n_local):
                # wartość z komórki "wstrzykiwana" do globalnej macierzy
                K_global[e.dof[i] - 1, e.dof[j] - 1] = K_global[e.dof[i] - 1, e.dof[j] - 1] + k_local[i, j]
    # Agregacja wektora obciążeń:
    F_global = sp.zeros(M_dim, 1)
    for i, l in enumerate(Glob_load): # i zwrca kolejność 0, 1, 2 natomiast l daje wartości odpowaidające i listy load_glob
        F_global[i,0] =  F_global[i,0] + l
    return K_global, F_global
# ====================
# Funkcja redukcji globalnych wektorów
# ====================
def dimention_reduction(K_global, F_global, Glob_constraint, M_dim):
    # Redukcja wymiaru macierzy i wektora obciąrzeń o warunki brzegowe:
    F_red = F_global.copy()
    K_red = K_global.copy() # Punktem wejściowym jest pełna macierz, .col_del modyfikuje macierz a chcemy nadal mieć pełną K_global
    for red in reversed(range(M_dim)): # odwrócona kolejność aby nie "psuć" indeksowania macierzy
        if Glob_constraint[red] == 1:
            K_red.row_del(red)
            K_red.col_del(red)
            F_red.row_del(red)
    return K_red, F_red
# ====================
# Funkcja wyświetlania latex:
# ====================
def latex_matrix_display(K_global, K_red, F_global, F_red, elements, angle_mesh_subs):
    # Schemat upraszczający formę macierzy sztywności:
    scalar = 1
    y_n = input("Try to simplify by fatoring (eg. E*I/l^3)? Y/N: ")
    if y_n.lower() == "y":
        if (base_element := next((el for el in elements if el.type == "2N4DOF_EB"), None)): # Zwraca pierwszy element belkowy (funkcja "any(e.type == "Spring" for e in elements):" zwróciłaby tylko czy jest taki element czy nie)
            scalar = 2 * base_element.mat.E * base_element.I() / base_element.L()**3
        elif (base_element := next((el for el in elements if el.type == "2N2DOF" or el.type == "2N2DOF_2D"), None)): # jak nie ma belkowego to sprawdza czy są pręty
            scalar = base_element.mat.E * base_element.A() / base_element.L()
        elif (base_element := next((el for el in elements if el.type == "Spring"), None)):
            scalar = 2 * base_element.k()
        if (base_element := next((el for el in elements if el.type == "2N2DOF_2D" or el.type == "Spring_2D" or el.type == "2N6DOF_2DF"), None)):
            y_n = input("Try to simplify by substituting angle values? Y/N: ")
            if y_n.lower() == "y":
                K_global = K_global.subs(angle_mesh_subs)
                K_red = K_red.subs(angle_mesh_subs)
    # Uproszczone macierze:
    K_global_display = sp.MatMul(scalar, (K_global / scalar).applyfunc(sp.simplify).applyfunc(sp.factor), evaluate=False)
    K_red_display = sp.MatMul(scalar, (K_red / scalar).applyfunc(sp.simplify).applyfunc(sp.factor), evaluate=False)
    # wyświetlanie:
    y_n = input("Display latex code for global stiffness matrix (K_global)? Y/N: ")
    if y_n.lower() == "y":
        print("==== Global stiffness matrix ====")
        print(sp.latex(K_global_display))
    y_n = input("Display latex code for reduced stiffness matrix (K_red)? Y/N: ")
    if y_n.lower() == "y":
        print("==== Reduced stiffness matrix ====")
        print(sp.latex(K_red_display))
    y_n = input("Display latex code for global load vector (F_global)? Y/N: ")
    if y_n.lower() == "y":
        print("==== Global load vector ====")
        print(sp.latex(F_global))
    y_n = input("Display latex code for reduced load vector (F_red)? Y/N: ")
    if y_n.lower() == "y":
        print("==== Reduced load vector ====")
        print(sp.latex(F_red))
    return K_global, K_red
# ====================
# Funkcja sprawdzająca kompletność symboli
# ====================
def validate_symbols(elements, F_red, Symbol_substitution):
    """Skanuje elementy siatki i wektor obciążeń, weryfikując obecność symboli w globalnym słowniku."""
    is_valid = True
    
    print("\n==== Symbol Validation ====")

    # 1. Sprawdzanie elementów (właściwości geometryczne)
    for e in elements:
        syms_to_check = []
        if hasattr(e, 'Area_Sym'): syms_to_check.append(e.Area_Sym)
        if hasattr(e, 'length_Sym'): syms_to_check.append(e.length_Sym)
        if hasattr(e, 'I_Sym'): syms_to_check.append(e.I_Sym)
        if hasattr(e, 'stif_Sym'): syms_to_check.append(e.stif_Sym)
        if hasattr(e, 'angle_Sym'): syms_to_check.append(e.angle_Sym)

        for sym in syms_to_check:
            # Upewniamy się, że to tekst i ignorujemy rezerwy typu "-" lub "0"
            if isinstance(sym, str) and sym not in [None, "", "-", "0"]:
                if sym not in Symbol_substitution:
                    print(f"ERROR: Symbol '{sym}' used in Element ID {e.id} is missing from symbol_substitutes!")
                    is_valid = False

    # 2. Sprawdzanie wektora obciążeń (obiekty SymPy)
    F_red_list = list(F_red)
    for index, load_expr in enumerate(F_red_list):
        # Pomijamy zera i liczby (dla nich .free_symbols może wyrzucić błąd lub dać pusty zbiór)
        # hasattr jest najbezpieczniejsze, upewnia się, że to obiekt SymPy
        if hasattr(load_expr, 'free_symbols'): 
            for sym in load_expr.free_symbols:
                sym_str = str(sym) # Konwersja obiektu SymPy (np. M_4) na tekst ("M_4")
                if sym_str not in Symbol_substitution:
                    print(f"ERROR: Load symbol '{sym_str}' at DOF index {index} is missing from symbol_substitutes!")
                    is_valid = False

    if is_valid:
        print("Result: OK! All symbols are accounted for.")
    else:
        print("Result: FAILED! Please update your .json files or numerical solution will yield incomplete results.")
        y_n = input("\nDo you want to proceed with calculations? Y/N: ")
        if y_n.lower() == "y":
            print("Continuing work, numerical solution will be compromised!")
            is_valid = True
        else:
            is_valid = False    
    return is_valid
# ====================
# Funkcja wyboru rozwiązania numerycznego/symbolicznego:
# ====================
def Symbols_numerical(K_red, F_red, Symbol_substitute):
    while True:
        choice = input("\n==== Pick displacement solution ====\n - numerical\n - symbolic\n - both\n - >").strip().lower()
        if choice.lower() == "numerical" or choice.lower() == "both":
            K_red_num = K_red.subs(Symbol_substitute)
            F_red_num = F_red.subs(Symbol_substitute)
            # Wybór jednostki długości
            while True:
                print("Available length units:")
                for Unit, loc_library in Unit_substitute.items():
                    if loc_library['type'] == 'length':
                        print(Unit)
                L_unit = input("Choose length unit: ")
                unit_found = False
                for Unit, loc_library in Unit_substitute.items():
                    if L_unit.lower() == Unit.lower() and loc_library['type'] == 'length':
                        L_unit = Unit
                        unit_found = True
                        print(f"Picked {Unit} ({loc_library['name']})")
                        break
                if unit_found == True:
                    break
                print("Unit not present in library")
            # Wybór jednostki kąta
            while True:
                print("Available angle units:")
                for Unit, loc_library in Unit_substitute.items():
                    if loc_library['type'] == 'angle':
                        print(Unit)
                Ang_unit = input("Choose angle unit: ")
                unit_found = False
                for Unit, loc_library in Unit_substitute.items():
                    if Ang_unit.lower() == Unit.lower() and loc_library['type'] == 'angle':
                        Ang_unit = Unit
                        unit_found = True
                        print(f"Picked {Unit} ({loc_library['name']})")
                        break
                if unit_found == True:
                    break
                print("Unit not present in library")
            # Wybór jednostki siły
            while True:
                print("Available force units:")
                for Unit, loc_library in Unit_substitute.items():
                    if loc_library['type'] == 'force':
                        print(Unit)
                Force_unit = input("Choose force unit: ")
                unit_found = False
                for Unit, loc_library in Unit_substitute.items():
                    if Force_unit.lower() == Unit.lower() and loc_library['type'] == 'force':
                        Force_unit = Unit
                        unit_found = True
                        print(f"Picked {Unit} ({loc_library['name']})")
                        break
                if unit_found == True:
                    break
                print("Unit not present in library")
            while True:
                print("Available torque units:")
                for Unit, loc_library in Unit_substitute.items():
                    if loc_library['type'] == 'torque':
                        print(Unit)
                Torque_unit = input("Choose force unit: ")
                unit_found = False
                for Unit, loc_library in Unit_substitute.items():
                    if Torque_unit.lower() == Unit.lower() and loc_library['type'] == 'torque':
                        Torque_unit = Unit
                        unit_found = True
                        print(f"Picked {Unit} ({loc_library['name']})")
                        break
                if unit_found == True:
                    break
                print("Unit not present in library")
            break
        if choice.lower() == "symbolic":
            K_red_num = None
            F_red_num = None
            L_unit = None
            Ang_unit = None
            break
        else:
            print("your solution type doesnt match provided ones")
            continue
    return choice, K_red_num, F_red_num, L_unit, Ang_unit, Force_unit, Torque_unit
# ====================
# Funkcja rozwiązywania układu równań:
# ====================
def U_displacement(K_red, F_red, M_dim, Glob_constraint):
    # Rozwiązanie układu równań:(Układ równań K x U = F (transpozycja K^T byłaby zapisana ablo sp.transpose(K_global) albo K_global.T))
    U_red = K_red.inv() @ F_red # Bo w SymPy .inv() robi M^-1
    # Tworzenie globalnego wektora przemieszczeń:
    U_glob = sp.zeros(M_dim, 1)
    red_row = 0 # zredukowany wiersz
    for i in range(M_dim):
        if Glob_constraint[i] == 0: # Wolny stopień swobody - pobieramy wartość z U_red
            U_glob[i, 0] = U_red[red_row, 0]
            red_row += 1 # Presunięcie indeksu zredukowanego w górę, aby nie pobrać tego samego z U_red
        else:
            pass # pass po prostu mówi aby python pominął to co się dziele za else, U_glob[i] dla else przyjmie wartość 0.
    U_glob = sp.simplify(U_glob)
    U_red = sp.simplify(U_red)
    U_glob = U_glob.as_mutable() # mutable pozwala na modyfikacje macierzy po jej uproszczeniu
    U_red = U_red.as_mutable()
    return U_glob, U_red
# ====================
# Funkcja wyznaczająca wektor sił
# ====================
def Reaction_calc(U_glob, K_glob):
    R_glob = K_glob @ U_glob
    return R_glob


# ====================
# Funkcja podstawiania jednostek pod przemieszczenia
# ====================
def symbol_subs(U_glob_num, R_glob_num, Glob_dof_type, L_unit, Ang_unit, Force_unit, Torque_unit, M_dim):
    U_glob_unit = U_glob_num.copy()
    R_glob_unit = R_glob_num.copy()
    for i in range(M_dim):
        # Sprawdzamy, czy typ zaczyna się od "U" (Translacja)
        if Glob_dof_type[i].startswith("U"):
            U_glob_unit[i, 0] = U_glob_unit[i, 0] * Unit_substitute[L_unit]["value"] * Unit_substitute[L_unit]["unit"]
            R_glob_unit[i, 0] = R_glob_unit[i, 0] * Unit_substitute[Force_unit]["value"] * Unit_substitute[Force_unit]["unit"]
        # Sprawdzamy, czy typ zaczyna się od "R" (Rotacja)
        elif Glob_dof_type[i].startswith("R"):
            U_glob_unit[i, 0] = U_glob_unit[i, 0] * Unit_substitute[Ang_unit]["value"] * Unit_substitute[Ang_unit]["unit"]
            R_glob_unit[i, 0] = R_glob_unit[i, 0] * Unit_substitute[Torque_unit]["value"] * Unit_substitute[Torque_unit]["unit"]
    return U_glob_unit, R_glob_unit
# ====================
# Funkcja rozwiązywania układu równań w połączeniu z wyborem rozwiązania:
# ====================
def U_solution(choice, K_global, K_red_num, F_red_num, K_red, F_red, M_dim, Glob_constraint, Glob_dof_type, L_unit, Ang_unit, Force_unit, Torque_unit, Symbol_substitute):
    if choice == "both":
        K_red_num = K_red_num.evalf()
        F_red_num = F_red_num.evalf()
        K_glob_num = K_global.subs(Symbol_substitute).evalf()
        U_glob, U_red = U_displacement(K_red, F_red, M_dim, Glob_constraint)
        U_glob_num, U_red_num = U_displacement(K_red_num, F_red_num, M_dim, Glob_constraint)
        R_glob = Reaction_calc(U_glob, K_global)
        R_glob_num = Reaction_calc(U_glob_num, K_glob_num)
        U_glob_unit, R_glob_unit = symbol_subs(U_glob_num, R_glob_num, Glob_dof_type, L_unit, Ang_unit, Force_unit, Torque_unit, M_dim)
    if choice == "symbolic":
        U_glob, U_red = U_displacement(K_red, F_red, M_dim, Glob_constraint)
        R_glob = Reaction_calc(U_glob, K_global)
        U_glob_num = U_red_num = U_glob_unit = R_glob_num = R_glob_unit = None
    if choice == "numerical":
        K_red_num = K_red_num.evalf()
        F_red_num = F_red_num.evalf()
        K_glob_num = K_global.subs(Symbol_substitute).evalf()
        U_glob_num, U_red_num = U_displacement(K_red_num, F_red_num, M_dim, Glob_constraint)
        R_glob_num = Reaction_calc(U_glob_num, K_glob_num)
        U_glob_unit, R_glob_unit = symbol_subs(U_glob_num, R_glob_num, Glob_dof_type, L_unit, Ang_unit, Force_unit, Torque_unit, M_dim)
        U_glob = U_red = R_glob = None
    return U_glob, U_red, U_glob_num, U_red_num, U_glob_unit, R_glob, R_glob_num, R_glob_unit
# ====================
# Funkcja wyświetlenia wyniku przemieszczeń i reakcji
# ====================
def display_solution(U_glob, U_red, U_glob_num, U_red_num, U_glob_unit, R_glob, R_glob_num, R_glob_unit):
    # Pakujemy wszystkie wektory i ich opisy do jednej listy
    # Format: ("Tytuł do wyświetlenia", zmienna_z_wektorem)
    vectors_to_print = [
        ("Symbolic global displacement vector", U_glob),
        ("Symbolic reduced displacement vector", U_red),
        ("Numerical global displacement vector (for SI units)", U_glob_num),
        ("Numerical reduced displacement vector (for SI units)", U_red_num),
        ("Numerical global displacement vector (with custom units)", U_glob_unit),
        ("Symbolic global force vector", R_glob),
        ("Numericalc global force vector (for SI units)", R_glob_num),
        ("Numericalc global force vector (with custom units)", R_glob_unit)
    ]

    while True:
        choice = input("\n==== Pick displacement solution formating ====\n - latex\n - pprint\n - both\n - > ").strip().lower()     
        if choice not in ["latex", "pprint", "both"]:
            print("Invalid choice, please try again.")
            continue 
        for title, vector in vectors_to_print: # title tyczy się pierwszej pozycji wektora a vector drugiej
            if vector is not None:
                print(f"\n==== {title} ====")
                # Obsługa formatu LaTeX
                if choice in ["latex", "both"]:
                    print("Latex:")
                    print(sp.latex(vector))
                    print() # Pusta linijka dla czytelności          
                # Obsługa formatu pprint
                if choice in ["pprint", "both"]:
                    print("pprint:\n")
                    sp.pprint(vector) # pprint wywołujemy "luzem", bo sam drukuje na ekran
                    print()
        break
# ==========================================
# STREFA 3: GŁÓWNY BLOK WYKONAWCZY (MAIN)
# ==========================================
if __name__ == "__main__":
    # Wywołanie pierwszej funkcji:
    starting_solver() 
    # Wywołanie funkcji wczytującej
    mesh_data = mesh_load(FOLDER_PATH) 
    # Szybkie sprawdzenie, czy funkcja poprawnie oddała dane
    if mesh_data:
        mesh_name = mesh_data["model_summary"]["mesh name"]
        print(f"\nImported mesh: {mesh_name}")
        # Wczytanie list elementów i węzłów oraz słowników z podstawieniami pod symbole
        node_list, element_list, mesh_type, general_mesh_subs, angle_mesh_subs = unpack_mesh(mesh_data)

        # sprawdzenie siatki, check mesh również przypisuje (załączenie funkcji)
        is_mesh_ok = check_mesh(node_list, element_list, material_library, mesh_type)
        
        if is_mesh_ok: 
            # Przypisanie stopni swobody do węzłów i elementów:      
            M_dim = assign_dofs(node_list, element_list)
            print(f"Global matrix dimension: {M_dim}x{M_dim}")
            # Tworzenie list stopni swobody:
            Glob_constraint, Glob_dof_type, Glob_dof_id = build_global_lists(node_list, M_dim)
            # Wczytanie obciążęń siatki:
            Glob_load, load_sym_subs = assign_loads(FOLDER_PATH_LOAD, node_list, mesh_name, M_dim)
            # Wyświetlenie list powiązanych ze stopniami swobody
            display_dof_lists(Glob_load, Glob_constraint, Glob_dof_type, Glob_dof_id)
            # Agregowanie Globalnej macierzy sztywności i wektora obciążeń:
            K_global, F_global = aggregate_global(element_list, M_dim, Glob_load)
            # Redukcja globalnej macierzy i wektora
            K_red, F_red = dimention_reduction(K_global, F_global, Glob_constraint, M_dim)
            # Tworzenie jednego wspólnego słownika podstawienia symboli, łączenie wszystkich słowników w jeden:
            Symbol_substitute = {**Base_Symbol_substitute, **general_mesh_subs, **load_sym_subs}
            # Walidacja powstałego słownika, czy pokrywa wszyskie symbole siatki oraz siatki obciążęń:
            is_symbol_ok = validate_symbols(element_list, F_red, Symbol_substitute)
            # Wyświetlanie uzyskanych macierzy/wektorów:
            K_global, K_red = latex_matrix_display(K_global, K_red, F_global, F_red, element_list, angle_mesh_subs)
            if is_symbol_ok:
                # Wybór typu rozwiązania:
                choice, K_red_num, F_red_num, L_unit, Ang_unit, Force_unit, Torque_unit = Symbols_numerical(K_red, F_red, Symbol_substitute)
                # Rozwiązanie układu równań:
                U_glob, U_red, U_glob_num, U_red_num, U_glob_unit, R_glob, R_glob_num, R_glob_unit = U_solution(choice, K_global, K_red_num, F_red_num, K_red, F_red, M_dim, Glob_constraint, Glob_dof_type, L_unit, Ang_unit, Force_unit, Torque_unit, Symbol_substitute)
                # Wyświetlenie rozwiązania równania:
                display_solution(U_glob, U_red, U_glob_num, U_red_num, U_glob_unit, R_glob, R_glob_num, R_glob_unit)
            else:
                print("\nStopped programme due to uncomplete symbol definitions. Closing program.")

        else:
            print("\nStopped programme due to compromised mesh data. Closing program.")
            
    else:
        print("\nFailed to read mesh. Closing program.")
