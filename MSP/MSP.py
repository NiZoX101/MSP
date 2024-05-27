import copy
T = ["!", "+", "*", "(", ")", "a", "b"]
N = ["A", "B", "K", "T", "Z", "M"]
#Вместо B' и T'- K и Z соответственно

productions = {
    "A": ["!B!"],
    "B": ["K"],
    "K": ["T", "K+T"],
    "T": ["Z"],
    "Z": ["M", "Z*M"],
    "M": ["a", "b", "(B)"]
}

# Создаем пустые множества L и R для каждого нетерминала
L = {nt: set() for nt in N}
R = {nt: set() for nt in N}

def LR_add():
    for nt, rules in productions.items():
        for rule in rules:
            # Добавляем самые левые символы в L(U)
            L[nt].add(rule[0])
            # Добавляем самые правые символы в R(U)
            R[nt].add(rule[-1])

    print("L(U) and R(U) for all nonterminals:")
    for nt in N:
        print(f"For nonterminal {nt}:")
        print(f"L({nt}): {', '.join(L[nt])}")
        print(f"R({nt}): {', '.join(R[nt])}")
    print("----------------------------------------")

    changed = True
    while changed:
        changed = False
        for nt in N:
            old_L = L[nt].copy()
            old_R = R[nt].copy()

            for nt2 in old_L:
                if nt2 != nt and nt2 not in T:
                    L[nt] |= L[nt2]
            
            for nt2 in old_R:
                if nt2 != nt and nt2 not in T:
                    R[nt] |= R[nt2]
                
            # Проверяем, изменились ли множества L(U) или R(U)
            if old_L != L[nt] or old_R != R[nt]:
                changed = True
    # Выводим результаты
    print("L(U) and R(U) for all nonterminals:")
    for nt in N:
        print(f"For nonterminal {nt}:")
        print(f"L({nt}): {', '.join(sorted(L[nt]))}")  # Сортируем множества для наглядности
        print(f"R({nt}): {', '.join(sorted(R[nt]))}")  # Сортируем множества для наглядности
        print()
# Заполняем множества L и R
LR_add()

prec_matrix = {symbol: {symbol2: '' for symbol2 in T+N} for symbol in T+N}

def fill_precedence_matrix():
    # Заполняем матрицу в соответствии с правилами предшествования
    for nt, rules in productions.items():
        for rule in rules:
            for i in range(1,len(rule)):
                # Если символы стоят рядом в правиле, ставим знак "=."
                prec_matrix[rule[i-1]][rule[i]] = '=.'

                if rule[i-1] in T and rule[i] in N:
                    for t_symbol in L[rule[i]]:
                        prec_matrix[rule[i-1]][t_symbol] = '<.'

                if rule[i-1] in N and rule[i] in T:
                    for n_symbol in R[rule[i-1]]:
                        prec_matrix[n_symbol][rule[i]] = '.>'

fill_precedence_matrix()
# Выводим результаты
print("Matrix of precedence relations:")
for symbol in T+N:
    print(f"{symbol}: {prec_matrix[symbol]}")

def build_linearization_graph():
    graph = {}  # Словарь для представления графа
    to_del = set()

    # Создаем вершины для каждого символа из алфавита (N+T)
    alphabet = N + T
    for symbol in alphabet:
        graph[(symbol,'-')] = set()
        graph[('-',symbol)] = set()

    # Обработка отношений из матрицы предшествования
    for row_symbol in alphabet:
        for col_symbol in alphabet:
            relation = prec_matrix[row_symbol][col_symbol]
            if relation == '=.':
                combined_vertex = (row_symbol, col_symbol)
                graph[combined_vertex] = set()
                to_del.add((row_symbol,'-'))
                to_del.add(('-',col_symbol))

    for key in to_del:
        del graph[key]

    for combined_vertex in list(graph.keys()):  # Преобразуем ключи в список для безопасной итерации
        for col in alphabet:
            if combined_vertex[0]!='-' and prec_matrix[combined_vertex[0]][col] == '.>':
                for check in list(graph.keys()):  # Преобразуем ключи в список для безопасной итерации
                    if check[1]==col:
                        graph[combined_vertex].add(check)
            elif combined_vertex[0]!='-' and prec_matrix[combined_vertex[0]][col]=='<.':
                for check in list(graph.keys()):
                    if check[1]==col:
                        graph[check].add(combined_vertex)

    print("Linearization Graph:")
    for node, neighbors in graph.items():
        if isinstance(node, tuple):
            node_str = f"({node[0]}, {node[1]})"
        else:
            node_str = f"{node}"
        neighbors_str = ', '.join(f"({n[0]}, {n[1]})" if isinstance(n, tuple) else f"{n}" for n in neighbors)
        print(f"{node_str}: {neighbors_str}")

    return graph

# Строим граф линеаризации
linearization_graph = build_linearization_graph()

def analyze_cycles(graph):
    copy_graph=copy.deepcopy(graph)
    while True:
        node_without_successors = None
        for node, neighbors in copy_graph.items():
            if not neighbors:
                node_without_successors = node
                break
        
        if node_without_successors is None:
            print("There are cycles")
            return False
        else:
            print(f"Edge has been removed {node_without_successors} ")
            del copy_graph[node_without_successors]
            for node, neighbors in copy_graph.items():
                if node_without_successors in neighbors:
                    neighbors.remove(node_without_successors)
                    
        if not copy_graph:
            print("There are no cycles!")
            return True
analyze_cycles(linearization_graph)
#print (linearization_graph)


def dfs(graph, start, visited=None, path_length=0, longest_path=0):
    if visited is None:
        visited = set()
    visited.add(start)

    # Обновляем длину текущего пути
    for next_vertex in graph[start]:
        if next_vertex not in visited:
            longest_path = dfs(graph, next_vertex, visited, path_length + 1, longest_path)

    # Обновляем длину наибольшего пути
    longest_path = max(longest_path, path_length)

    # После завершения обхода снимаем вершину со стека
    visited.remove(start)

    return longest_path


def f(graph,si):
    max_length=0
    for S in graph.keys():
        #print(S[0])
        #print(si)
        if S[0]==si[0]:
            if si[0]=='-':
                print("Sry, it's Gj variable")
                return
            lp=dfs(graph, S)
            if lp>max_length:
                max_length=lp
    return max_length

def g(graph,si):
    max_length=0
    for S in graph.keys():
        #print(S[0])
        #print(si)
        if S[1]==si[1]:
            if si[1]=='-':
                print("Sry, it's Fi variable")
                return
            lp=dfs(graph, S)
            if lp>max_length:
                max_length=lp
    return max_length

def f_all(graph):
    fall={}
    for i in T+N:
        fall[i]=f(graph,(i,'-'))
    return fall

def g_all(graph):
    gall={}
    for i in T+N:
        gall[i]=g(graph,('-',i))
    return gall

# Пример использования
#start_node = ('-', 'K')  # Начальная вершина для поиска наибольшего пути
#longest_path = g(linearization_graph, start_node)
#print(f"The longest way: {start_node[0]}: {longest_path}")

# Пример использования
#result_gall = f_all(linearization_graph)
#print(result_gall)
def precedence_relation(symbol1, symbol2):
    if prec_matrix[symbol1][symbol2] != '':
        return prec_matrix[symbol1][symbol2]
    return None

def has_precedence(symbol1, symbol2):
    if precedence_relation(symbol1, symbol2) is not None:
        return True
    return False

# Пример использования
symbol1 = 'K'
symbol2 = '+'
if has_precedence(symbol1, symbol2):
    print(f"{symbol1} has precedence over {symbol2}")
else:
    print(f"No precedence relation between {symbol1} and {symbol2}")

def search_prod(str1):
    num = 1  # Начинаем с 1, так как правила начинаются с 1
    for symb in productions.keys():
        for rule in productions[symb]:
            if rule == str1:
                return num
            num += 1
    return -1  # Возвращаем -1, если правило не найдено

def search_symb(num):
    n = 1  # Начинаем с 1, так как правила начинаются с 1
    for s in productions:
        n += len(productions[s])
        if n > num:
            return s
    return None  # Возвращаем None, если номер правила неверен или не найден

print("f(s):",f_all(linearization_graph))
print("g(s):",g_all(linearization_graph))

def parser(input_str):
        stack = []
        output=[]
        stack.append(input_str[0])
        input_str=input_str[1:]
        print("Input:",input_str)
        if stack[0]!='!':
            print('Incorrect input!')
            return
        while stack[0]!="A" and input_str:
            #print(stack)
            #print(input_str)
            #print("preobraz:")
            if has_precedence(stack[len(stack)-1],input_str[0])==False:
                print(f"No precedence relation between {stack[len(stack)-1]} and {input_str[0]}")
                return 
            if f(linearization_graph,(stack[len(stack)-1],'-'))<=g(linearization_graph,('-',input_str[0])):
                stack.append(input_str[0])
                print(stack)
                input_str=input_str[1:]
                print(input_str)
            elif f(linearization_graph,(stack[len(stack)-1],'-'))>g(linearization_graph,('-',input_str[0])):
                i=len(stack)-1
                while i>0 and f(linearization_graph,(stack[i-1],'-'))==g(linearization_graph,('-',stack[i])):
                    i-=1
                #print("IIIII:",i)
                str1=''.join(stack[i:])
                ind=search_prod(str1)
                output.append(ind)
                del stack[i:]
                stack.append(search_symb(ind))
        str1=''.join(stack)
        ind=search_prod(str1)
        output.append(ind)
        return output
# Тестирование
input_str = "!a(b+a()!"
print(parser(input_str))