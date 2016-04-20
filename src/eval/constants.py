
CLASSIFICATION_TYPES = ['standard', 'misspelled', 'confused', 'incomplete', 'combined', 'user-identified',
                        'unrecovered', 'part-of-speech', 'lexical entry']
LABELS = {0: ('standard', 0), 1: ('misspelled', 1), 2: ('confused', 1), 3: ('incomplete', 2), 4: ('combined', 2),
          5: ('user-identified', 3), 6: ('unrecovered', 3), 8: ('part-of-speech', 3), 9: ('lexical entry', 3)}
LABEL_TEXT = [(0, 'standard'), (1, 'misspelled'), (2, 'confused with another gloss'),
              (3, 'a lexical entry that should be glossed'), (4, 'a combination that should be divided'),
              (5, 'author-defined and specific to the language\'s IGT'), (6, 'an unrecoverable gloss'),
              (8, 'a part-of-speech tag or other non-gram value'), (9, 'a lexical entry')]

INFER_BASELINE = {('tense', 'past'): True,
                  ('tense', 'future'): True,
                  ('tense', 'present'): True,
                  ('aspect', 'perfective'): True,
                  ('aspect', 'imperfective'): True
                  }