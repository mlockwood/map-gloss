## I/O
grams, values, gold standard DataModelTemplate conversion with JSON from csv

models, choices, dataset, lexicon DMT

separate map_gloss as a general tool and the model runs that validate it

convert references to large files by model that use DMT

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

## Gold Standard
What to do with words in IGT that are actually multiple grams? Essentially what to do with combined and incomplete?

Remember to separate grams and classification label, fix this using set_object_attrs()


## Model
Move Containers and UniqueGloss to Model; result = {"dev1": {"iso": [{"gold", "input", "final"}, ..]}}

As a temporary measure final will point to a {} that used to be represented in UniqueGloss, then when the final weight
scheme is applied the final answer will be stored there.

Then create a new function(s) that iterates through a model, builds dictionaries as needed and then sends them to
confusion matrices. Once the Compare is called ouput the results to the appropriate the location.

Reference could then just be a dictionary in memory created by [input]: final.

TBL could be its own script where it returns a dictionary of {dataset: {iso: {gloss: result} which then gets reformatted
to fit {dataset: {iso: {gloss: {final: {tbl: result}}}}}

RECHECK all vector processing, clarify is it [{vector}] or {id: {vector}}

Is result weights the same as model.classifiers?
