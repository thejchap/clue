# clue

## overview

clue sat solver with a simple API

## usage

### api

```zsh
make server
open http://localhost:8000/docs
```

### cli

todo. currently just takes an existing game id and prints notepad

```zsh
➜  clue git:(main) python main.py notepad ea3aea32-00b6-43c7-9d67-da8adf23147a
              file  scarlett green mustard plum peacock white
scarlett         -         0     -       -    -       -     -
green            -         0     -       -    -       -     -
mustard          -         0     -       -    -       -     -
plum             -         0     -       -    -       -     -
peacock          -         0     -       -    -       -     -
white            -         0     0       0    -       -     -
candlestick      -         0     -       -    -       -     -
dagger           0         1     0       0    0       0     0
pipe             -         0     0       0    -       -     -
revolver         -         0     -       -    -       -     -
rope             -         0     -       -    -       -     -
wrench           -         0     -       -    -       -     -
kitchen          0         1     0       0    0       0     0
ballroom         -         0     -       -    -       -     -
conservatory     -         0     -       -    -       -     -
dining_room      -         0     -       -    -       -     -
cellar           -         0     -       -    -       -     -
billiard_room    -         0     -       -    -       -     -
library          -         0     -       -    -       -     -
lounge           -         0     -       -    -       -     -
hall             -         0     0       0    -       -     -
study            -         0     -       -    -       -     -
```

## sources

- http://logic.stanford.edu/intrologic/extras/satisfiability.html
- https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.627.3292&rep=rep1&type=pdf
- https://en.wikipedia.org/wiki/Conjunctive_normal_form
- https://davefernig.com/2018/05/07/solving-sat-in-python/
- https://www.notion.so/Clue-solver-8686d0c92c664c8fa9f865b9b22426cd#abb1d829dbe342ceb1ae8902d4414593
- http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.610.2876&rep=rep1&type=pdf
- https://en.wikipedia.org/wiki/Influence_diagram
