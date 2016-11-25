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

gold standard is an extension of this same process because it is relevant to the XIGT and choices the user loads as is
the lexicon and models -- therefore the only data inherent to map_gloss is the standard_grams and standard_values


models
0x1,dev1&dev2,test,tbl@1.0
0x2,dev1&dev2&test,<cross>,tbl@1.0
0x3,dev1!rus&dev2&test,dev1-rus,tbl@1.0
