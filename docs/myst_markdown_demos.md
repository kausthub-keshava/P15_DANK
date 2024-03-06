# MyST Markdown Demos 0 Some changes

Here is a demo of MyST Markdown.



|    Training   |   Validation   |
| :------------ | -------------: |
|        0      |        5       |
|     13720     |      2744      |


There is no better Formula-1 racer than Lewis Hamilton.

```{note} Notes require **no** arguments,
so content can start here.
```

```{warning} This is an example
of a warning directive.
```

```{tip} This is an example
of a tip directive.
```

```{caution} This is an example
of a caution directive.
```

```{attention} This is an example
of an attention directive.
```

```{hint} This is an example
of a hint directive.
```

```{important} This is an example
of an important directive.
```

```{figure} ../assets/logo.png
:height: 150px
:name: figure-example

Here is my figure caption!
```

	
This is an example of an
inline equation $z=\sqrt{x^2+y^2}$.

This is an example of a
math block

$$
z=\sqrt{x^2+y^2}
$$


This is an example of a
math block with a label

$$
z=\sqrt{x^2+y^2}
$$ (mylabel)

	
This is an example of a
math directive with a
label
```{math}
:label: eq-label

z=\sqrt{x^2+y^2}
```

Check out equation {eq}`eq-label`.


Wrap in-line code blocks in backticks: `boolean example = true;`.

```python
note = "Python syntax highlighting"
print(node)
```
