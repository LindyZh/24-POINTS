#  Write the function get_target which returns a string that contains an expression that uses all the numbers
#  in the list once, and results in the target. The expression can contain parentheses. Assume that the task
#  is possible.
#  For example, get_target([1, 5, 6, 7], 21) can return "6/(1-5/7)". This will return all permutation of the
#  list of number.
import copy
############################################# 数学表达式生成函数 #############################################
def generate_comb_op(n):
    '''find all combination of Arithmetic operators with n possible spaces for operators'''
    # 建立base case
    if n == 0:
        return []  # 当n为0时不返回任何操作符号
    elif n == 1:
        return [['+'], ['-'], ['*'], ['/']]  # 当n为1时返回基础的四个符号，注意这里需要用到list of list
    op_list = generate_comb_op(n - 1)  # 因为之后要加，所以我们这里用到递归的逻辑，来找到最基本的operator_list
    all_op_list = []  # 新建一个list来准备更新我们加了运算符号后的sublist
    # 最后我们还是要用循环的逻辑来给我们原来list里的元素加新的符号
    for i in op_list:
        for j in ['+', '-', '*', '/']:
            all_op_list.append(i + [j])  # 这里用了新的list，来确保每个sublist的长度是相等的
    return all_op_list  # 最后返回最终结果


def generate_permutated_list(num_list):
    '''find permuted lists of n given numbers'''
    # 建立base case
    if len(num_list) == 0:
        return []  # 当n为0时不返回任何数字
    if len(num_list) == 1:
        return [num_list]  # 当n为1时返回所有式子，作为之后首数字的基础
    list_of_comb = []  # 新建列表来存更新的排列
    for i in range(len(num_list)):
        first_num = num_list[i]  # 生成首字母
        for j in generate_permutated_list(num_list[:i] + num_list[i + 1:]):  # 去除首字母，继续递归
            list_of_comb.append([first_num] + j)  # 加入新的list

    return list_of_comb  # 最后返回最终结果


#################################### 定义所有可能出现的数学操作，包括加减乘除 ####################################

def division(a, b):  # 除法比较特殊，用了try except来考虑到被除数为0的情况
    try:
        return a / b
    except:
        return ''

def multiply(a, b):
    return a * b

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

############################################ 数学表达式处理函数 ##############################################

def modify_op(equation, op):
    '''this function modify the given equation by only computing the section with the given operators
    parameters:
        equation: a list that represents a given mathematical equation which may or may not contain the
                given numerical operators. Ex, ['1','+','2'] represents the equation 1+2
        op: a string that is the given numerical operators'''

    # 这里我们把代表数学计算的字符串和以上定义的操作函数的名字以字典的方式联系并储存起来
    operators = {'/': division, '*': multiply, '+': add, '-': subtract}

    while op[0] in equation or op[1] in equation:  # 用while循环来确保没有遗漏任何字符
        min_index = 1000000
        op_0 = 1000000
        if op[0] in equation:
            op_0 = equation.index(op[0])  # 找到表达式内的第一处需要计算的字符位置
        # 把表达式需要计算的部分替换成计算结果
        op_1 = 1000000
        if op[1] in equation:
            op_1 = equation.index(op[1])
        if op_1 < op_0:
            min_index = op_1
            min_op = op[1]
        else:
            min_index = op_0
            min_op = op[0]

        if equation[min_index + 1] != '' and equation[min_index - 1] != '':
            equation[min_index - 1:min_index + 2] = [
                str(operators[min_op](float(equation[min_index - 1]), float(equation[min_index + 1])))]  # 注意这里调用了前面字典里储存的函数名
            # print(equation[min_index - 1:min_index + 2])
        else:
            return ['']
    return equation  # 返回结果


def evaluate(equation):
    '''updated version of the evaluation function, place the original loop in a recursive structure.'''

    for i in range(len(equation)):
        if type(equation[i]) == list:  # 如果表达式类型为list
            equation[i] = evaluate(equation[i])  # 满足括号条件，开始递归

    equation = modify_op(equation, ['/', '*'])  # 使用helper function
    equation = modify_op(equation, ['+', '-'])
    # print(equation[0])

    return equation[0]  # 最后返回最终计算结果


############################################# 括号位置生成函数 #############################################

def layer_sort(equation, depth=3):  # 默认凑对的长度为3（这里是因为两个数字加一个运算符号有三位数）
    '''generate all possible brackets combination within a recursive layer'''
    if depth == len(equation):  # 如果凑对长度达到表达式总长，便返回表达式原式
        return []
    layer_comb = []  # 初始化一个总列表

    # 我们要从最左边开始定义左括号的位置，然后在相应长度的结束定义右括号的位置
    # len(equation)-depth+1 为最右边的左括号合理位置+1，是循环的结束位置
    for i in range(0, len(equation) - depth + 1, 2):  # 间隔为2，因为我们要跳过一个数字和一个符号
        new_equation = equation[:i] + [equation[i:i + depth]] + equation[i + depth:]  # 写出新表达式
        layer_comb.append(new_equation)
    for j in layer_sort(equation, depth + 2):
        layer_comb.append(j)
    return layer_comb


def generate_all_brackets(equation):
    '''get all bracket combination from the the given equation in list form'''

    layer_possibility = layer_sort(equation)  # 找到本层可用的表达式
    all_possibility = layer_possibility[:]
    for i in layer_possibility:
        if len(i) > 3:  # 检查是否达成递归条件，这一步同时也是这个递归函数的base case
            next_layer_equ = generate_all_brackets(i)
            for j in next_layer_equ:  # 去重操作
                if j not in all_possibility:
                    all_possibility.append(j)

    return [equation] + all_possibility  # 不要忘了在列表最开始加入原式


########################################### 字符串格式转换函数 #############################################

def convert_to_str(equation_list):
    equation = ''  # 初始化字符串表达式
    for i in range(len(equation_list)):
        if type(equation_list[i]) == list:  # 这里是递归条件，如果数据类型为list，我们要把括号内的表达式传到下一层
            equation += '(' + convert_to_str(equation_list[i]) + ')'  # 加入括号
        else:
            equation += equation_list[i]  # base case， 如果数据类型不是list，那么就普通返回字符串
    return equation  # 返回字符串形式的表达式

def convert_to_latex(equation_list):
    equation = ''  # 初始化字符串表达式
    for i in range(len(equation_list)):
        if type(equation_list[i]) == list:  # 这里是递归条件，如果数据类型为list，我们要把括号内的表达式传到下一层
            equation += '(' + convert_to_str(equation_list[i]) + ')'  # 加入括号
        else:
            equation += equation_list[i]  # base case， 如果数据类型不是list，那么就普通返回字符串
    return equation  # 返回字符串形式的表达式

############################################# 最终使用函数 ################################################

def get_target(num_list, target):
    op_list = generate_comb_op(len(num_list) - 1)  # 找出所有加减乘除的排列组合
    num_comb = generate_permutated_list(num_list)  # 找出所有数字的排列组合
    # 用for嵌套循环来整合所有表达式可能
    for each_op_list in op_list:
        for each_num_list in num_comb:
            equation = []
            equation_list = []  # 初始化基础表达式，以及基础+括号表达式
            for i in range(len(each_op_list)):
                equation.extend([str(each_num_list[i]), each_op_list[i]])
            equation.append(str(each_num_list[-1]))  # 组装基础表达式
            equation_list.append(equation)  # 把基础表达式加入基础+括号表达式的列表
            equation_list.extend(generate_all_brackets(equation))  # 把所有括号表达式加入括号表达式的列表

            n = 0
            for index in range(len(equation_list)):
                each_equation = equation_list[index]
                n += 1
                equation_str = convert_to_str(each_equation)  # 先把列表转化成字符串
                # print('the equation string is',equation_str)
                if evaluate(copy.deepcopy(each_equation)) == str(float(target)):# 如果最终结果相等便返回字符串
                    return equation_str
    return -1
def translate_to_latex(num_list,target):
    string = get_target(num_list,target)
    if string != -1:
        string = string.replace('*',' &times ').replace('/', '\div')
    return string

if __name__ == '__main__':
    print(translate_to_latex([10,2,5,8],24))
    # print(evaluate(['10', '-', '2', '+', '5']))
    # bug fixed:
    # 1) operation order fixed
    # 2) calculation issues regarding list aliasing fixed by using deep copy