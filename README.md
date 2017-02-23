# PORTHOS: A tool to compare the behavior of programs against different memory models

![myimage-alt-tag](https://github.com/hernanponcedeleon/PORTHOS/blob/master/extras/porthos.jpg)

Usage
======

```
./porthos.py -i <input> -s <source> -t <target>
```

where \<input> must be a .litmus or .pts (see below) program and \<source>, \<target> must be one of the following MCMs: 
- sc
- tso
- pso
- rmo
- alpha
- power
- cav10

The .pts format:
======

```
  program ::= {⟨loc*⟩} ⟨thrd*⟩

  ⟨thrd⟩ ::= thread String {⟨inst⟩}

  ⟨inst⟩ ::= ⟨com⟩ | ⟨inst⟩; ⟨inst⟩ | while ⟨pred⟩ ⟨inst⟩ | if ⟨pred⟩ ⟨inst⟩ else ⟨inst⟩

  ⟨com⟩ ::= ⟨reg⟩ ← ⟨expr⟩ | ⟨reg⟩ ← ⟨loc⟩ | ⟨loc⟩ = ⟨reg⟩ | ⟨fence⟩
  
  ⟨fence⟩ ::= hfence | lfence | cfence
  
  ⟨pred⟩ ::= ⟨expr⟩ | ⟨pred⟩ and ⟨pred⟩ | ⟨pred⟩ or ⟨pred⟩ | not ⟨pred⟩ 
  
          | ⟨expr⟩ == ⟨expr⟩ | ⟨expr⟩ != ⟨expr⟩
          
          | ⟨expr⟩ < ⟨expr⟩ | ⟨expr⟩ <= ⟨expr⟩
          
          | ⟨expr⟩ > ⟨expr⟩ | ⟨expr⟩ >= ⟨expr⟩
  
  ⟨expr⟩ ::= Int | ⟨reg⟩
  
          | ⟨expr⟩ + ⟨expr⟩ | ⟨expr⟩ - ⟨expr⟩
  
          | ⟨expr⟩ * ⟨expr⟩ | ⟨expr⟩ / ⟨expr⟩
          
          | ⟨expr⟩ % ⟨expr⟩ 
  ```
