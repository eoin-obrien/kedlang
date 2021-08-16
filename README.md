# Ked

Ked is the first programming language known to hail from [The People's Republic of Cork][cork].
It was first discovered and partially described by [Adam Lynch][adam-lynch] at https://adam-lynch.github.io/ked/.
`kedlang` is an attempt at creating a lexer, parser and interpreter for Ked with a few additions and guesses to round out the language.

[cork]: http://en.wikipedia.org/wiki/Cork_(city)
[adam-lynch]: https://github.com/adam-lynch

## Description

The Ked interpreter can be installed using `pip`.

```shell
$ pip install kedlang
```

Ked scripts are executed by passing them to the interpreter.

```shell
$ kedlang script.ked
```

## Disclaimer

This is very much a work in progress, and as such is practically guaranteed to be riddled with all kinds of interesting and convoluted quirks and bugs. For the love of Cork, don't try to use this in production. Or in development. Or anywhere, really.

## Note

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
