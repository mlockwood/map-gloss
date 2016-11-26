## I/O
grams, values, gold standard DataModelTemplate conversion with JSON from csv

models, choices, dataset, lexicon DMT

separate map_gloss as a general tool and the model runs that validate it

### File Collection for XIGT and Choices
how does a user point map gloss to their datasets/choices?
[
  {
    "name": "dev1"
    "path": "/aggregation/data/dev1"
  }
]

then infer by iso/testsuite-enriched.xml and iso/choices.up etc

### Parameters

internal: grams, values
internal or loaded: gold standard, lexicon
loaded: datasets, model


models
0x1,dev1&dev2,test,tbl@1.0
0x2,dev1&dev2&test,<cross>,tbl@1.0
0x3,dev1!rus&dev2&test,dev1-rus,tbl@1.0
