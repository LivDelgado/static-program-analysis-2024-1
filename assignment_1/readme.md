## Description

Throughout this course, we shall be using a very simple programming language to implement some concepts learned in the classroom. This programming language contains, initially, five types of instructions:

- Add(x, a, b): implements x = a + b
- Mul(x, a, b): implements x = a * b
- Lth(x, a, b): implements x = (a < b) ? 1 : 0
- Geq(x, a, b): implements x = (a >= b) ? 1 : 0
- Bt(x, i0, i1): if x != 0, then executes instruction i0, else executed i1

This programming language is very simple, but it is [Turing Complete](https://en.wikipedia.org/wiki/Turing_completeness): you can write any computable function using these instructions. Every instruction has a "next" field, which is the next instruction that should be executed. Branches (Bt), in turn, have two next fields (the two possible execution paths). 

An interpreter for this programming language is quite simple. There is a prototype below:

```python
def interp(instruction, environment):
	if instruction:
		instruction.eval(environment)
		return interp(instruction.get_next(), environment)
	else:
		return environment
```

The interpreter receives an instruction (which might have a next field), plus an environment. The environment is a table that maps variable names (strings) to values (integers). As an example, the code below should work without raising an error:

```python
env = Env({"m": 3, "n": 2, "zero": 0})

m_min = Add("answer", "m", "zero")

n_min = Add("answer", "n", "zero")

p = Lth("p", "n", "m")

b = Bt("p", n_min, m_min)

p.add_next(b)

assert(interp(p, env).get("answer") == 2)
```

In this VPL, you must implement three new functions, using the instructions in our programming language:

- test_min3(x, y, z): returns the minimum of x, y and z ✅
    
    ```python
    def test_min3(x, y, z):
        """
        Stores in the variable 'answer' the minimum of 'x', 'y' and 'z'
    
        Examples:
            >>> test_min3(3, 4, 5)
            3
    
            >>> test_min3(5, 4, 3)
            3
        """
        env = Env({"x": x, "y": y, "z": z, "zero": 0})
        
        # this will be the answer if x is the minimum
        x_min = Add("answer", "x", "zero")
        
        # this will be the answer if y is the minimum
        y_min = Add("answer", "n", "zero")
        
        # this will be the answer if z is the minimum
        z_min = Add("answer", "z", "zero")
        
        x_lth_z = Lth("x_lth_z", "x", "z")
        y_lth_x = Lth("y_lth_x", "y", "x")
        y_lth_z = Lth("y_lth_z", "y", "z")
        
        if_y_lth_z = Bt("y_lth_z", y_min, z_min)
        if_y_lth_x = Bt("y_lth_x", y_min, x_min)
        if_x_lth_z = Bt("x_lth_z", if_y_lth_x, if_y_lth_z)
        
        x_lth_z.add_next(y_lth_x)
        y_lth_x.add_next(y_lth_z)
        y_lth_z.add_next(if_x_lth_z)
        interp(x_lth_z, env)
        return env.get("answer")
    ```
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/dfa6d688-a600-44fd-8c02-3a93959f964a/b1bb30de-1fec-4997-9ec6-bd89b71f2324/Untitled.png)
    
- test_div(m, n): returns the integer division of m by n.
    
    ```python
    Div(x, a, b):
        if b == 0:  # check if the divisor is zero
            x = 0
        else:
            counter = 0
            while Geq(x, a, b):
                x = Sub(x, b, a)
                counter = Add(counter, 1, 0)
            # set x to the remainder
            x = a
            # return the quotient
            counter
     
    ```
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/dfa6d688-a600-44fd-8c02-3a93959f964a/2c8aaca9-de8d-4fda-94da-24a453f8a104/Untitled.png)
    
    ```python
    def test_div(m, n):
        """
        Stores in the variable 'answer' the integer division of 'm' and 'n'.
    
        Examples:
            >>> test_div(30, 4)
            7
    
            >>> test_div(4, 3)
            1
    
            >>> test_div(1, 3)
            0
        """
        env = Env({
            "divisor": n,
            "x": 0,
            "quociente": 0,
            "dividendo": m,
            "resto": 0,
            "zero": 0,
            "menosUm": -1,
            "um": 1
        })
    
        resposta_quociente = Add("answer", "quociente", "zero")
    
        comparacao_dividendo_divisor = Geq("comparacao_dividendo_divisor", "dividendo", "divisor")
    
        # fazer dividendo = dividendo - divisor
        inverso_divisor = Mul("inverso_divisor", "divisor", "menosUm")
        dividendo_menos_divisor = Add("dividendo_menos_divisor", "dividendo", "inverso_divisor")
        novo_dividendo = Add("dividendo", "dividendo_menos_divisor", "zero")
        
        incrementa_quociente = Add("quociente", "quociente", "um")
        
        comparacao_dividendo_divisor_verdadeira = Bt("comparacao_dividendo_divisor", inverso_divisor, resposta_quociente)
    
        resposta_zero = Add("answer", "zero", "zero")
        divisao_por_zero = Bt("divisor", comparacao_dividendo_divisor, resposta_zero)
    
        resposta_zero.add_next(divisao_por_zero)
    
        comparacao_dividendo_divisor.add_next(comparacao_dividendo_divisor_verdadeira)
        inverso_divisor.add_next(dividendo_menos_divisor)
        dividendo_menos_divisor.add_next(novo_dividendo)
        novo_dividendo.add_next(incrementa_quociente)
        incrementa_quociente.add_next(comparacao_dividendo_divisor)
    
        interp(resposta_zero, env)
    
        return env.get("answer")
    ```
    
- test_fact(n): returns the factorial of n.
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/dfa6d688-a600-44fd-8c02-3a93959f964a/b523ccb6-b5be-46a7-a676-6af60f1c6679/Untitled.png)
    
    ```python
    def test_fact(n):
        """
        Stores in the variable 'answer' the factorial of 'n'.
    
        Examples:
            >>> test_fact(3)
            6
        """
        env = Env({"atual": n, "n": n, "zero": 0, "um": 1, "menosUm": -1, "dois": 2, "acumulo": n})
    
        resposta_um = Add("answer", "um", "zero")
        resposta_acumulo = Add("answer", "acumulo", "zero")
    
        comparacao_atual = Geq("comparacao_atual", "atual", "dois")
        nova_iteracao = Add("x", "atual", "menosUm")
        multiplicacao = Mul("multi", "acumulo", "x")
        novo_acumulo = Add("acumulo", "multi", "zero")
        atualiza_atual = Add("atual", "x", "zero")
    
        valida_comparacao_atual = Bt("comparacao_atual", nova_iteracao, resposta_acumulo)
    
        n_geq_2 = Geq("n_geq_2", "n", "dois")
        valida_n_geq_2 = Bt("n_geq_2", nova_iteracao, resposta_um)
    
        n_geq_2.add_next(valida_n_geq_2)
        nova_iteracao.add_next(multiplicacao)
        multiplicacao.add_next(novo_acumulo)
        novo_acumulo.add_next(atualiza_atual)
        atualiza_atual.add_next(comparacao_atual)
        comparacao_atual.add_next(valida_comparacao_atual)
        
        interp(n_geq_2, env)
    
        return env.get("answer")
    ```
    

The VPL contains a file, `todo.py`, which you must implement. That file contains an example that you can use: the function `test_min`, which computes the minimum of two numbers. The VPL consists of three files: `todo.py`, `lang.py` and `driver.py`. You must upload these three files. Except for `driver.py`, the other files use doctests, so that you can check that everything is correct doing:

`python3 -m doctest lang.py # or python3 -m doctest todo.py`