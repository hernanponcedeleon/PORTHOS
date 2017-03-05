# PORTHOS: A tool to compare the behavior of programs against different memory models

![myimage-alt-tag](https://github.com/hernanponcedeleon/PORTHOS/blob/master/extras/porthos.jpg)

Requirements
======
- pyparsing package (http://pyparsing.wikispaces.com)

Usage
======

```
./porthos.py -s <source> -t <target> -i <input> [-o, --print=]
```

where \<input> must be a .litmus or .pts (see below) program and \<source>, \<target> must be one of the following MCMs: 
- sc
- tso
- pso
- rmo
- alpha
- power
- cav10

The optional -o and flags produces a .dot file showing the basic relations **rf**, **ws**, **fr** and **po** (dashed po relation shows the difference between source and target models). Additional relations can be displayed in the graph using --print=r1,r2,...,rn.

The .pts format:
======

Examples are provided in the **benchmarks/** folder.
```
  program ::= {⟨loc⟩*} ⟨thrd⟩*

  ⟨thrd⟩ ::= thread String {⟨inst⟩}

  ⟨inst⟩ ::= ⟨com⟩ | ⟨inst⟩; ⟨inst⟩ | while ⟨pred⟩ {⟨inst⟩} | if ⟨pred⟩ {⟨inst⟩} else {⟨inst⟩}

  ⟨com⟩ ::= ⟨reg⟩ <- ⟨expr⟩ | ⟨reg⟩ <- ⟨loc⟩ | ⟨loc⟩ = ⟨reg⟩ | ⟨fence⟩
  
  ⟨fence⟩ ::= hfence | lfence | cfence
  
  ⟨pred⟩ ::= Bool | ⟨pred⟩ and ⟨pred⟩ | ⟨pred⟩ or ⟨pred⟩ | not ⟨pred⟩ 
  
          | ⟨expr⟩ == ⟨expr⟩ | ⟨expr⟩ != ⟨expr⟩
          
          | ⟨expr⟩ < ⟨expr⟩ | ⟨expr⟩ <= ⟨expr⟩
          
          | ⟨expr⟩ > ⟨expr⟩ | ⟨expr⟩ >= ⟨expr⟩
  
  ⟨expr⟩ ::= Int | ⟨reg⟩
  
          | ⟨expr⟩ + ⟨expr⟩ | ⟨expr⟩ - ⟨expr⟩
  
          | ⟨expr⟩ * ⟨expr⟩ | ⟨expr⟩ / ⟨expr⟩
          
          | ⟨expr⟩ % ⟨expr⟩ 
  ```
