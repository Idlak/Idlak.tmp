.. _language-resources:

#########
Languages
#########

Idlak has been designed to work with and provide examples in multiple languages.
Generally languages are refered to by their languages codes in programs.

* Language (lng) codes are `2 letter ISO_639-1 codes <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_
* Accent (acc) codes are 2 ASCII letters, see :ref:`accents`

A note on archectures: In Idlak we allow for multiple versions of resources to
sit along side one another. These are called archectures and are
in the language resource xml names after the final "-".
Idlak requires that the default archecture be defined so the file
names below all have a ``-default.xml`` ending. In general Idlak
can choose alternative archectures for individual resources.

***********************
Creating a new language
***********************

The sections below explain the required resources for languages.
Some of the resources are accent specific, these have been marked.
In general all language resources can be overridden by specific accents.

Phoneset
========

.. code-block:: none

    idlak-data/<lng>/<acc>/phoneset-default.xml

*Accent specific*

In IPA there would be multiple ways to write "r" in English, that are from a comprehension
point of view the same, but a statistical model would need to learn all of them
seperately. Alternatively nasalisation does not affect English phonemes, but they do for French.
For this reason in Idlak we use limited phonesets for each accent.
This prevents the explosion of data requirements.

Within Idlak phonemes are lower case ASCII letters, normally limited
to three characters. Numbers are used for stress and tone, so cannot be part
of a phoneme name. As much as possible different accents should use the same
symbols for equivalent phonemes.

The format for the phoneset is as follows:

.. code-block:: xml

  <?xml version="1.0"? encoding="utf-8">
  <phoneset language="" accent="" >
      <phone name="" ipa="" example-word="" example-pron="" syllabic="" />
      ...
  </phoneset>


Where

* **name** - The ASCII name of the phoneme
* **ipa** - The cannonical IPA representation, it should be noted that multiple IPA symbols
            can be mapped onto this phoneme, but this is what should be considered the representative
            pronounciation.
* **example-word** - The cannonical example word for the phoneme
* **example-pron** - The full pronounciation for the example
* **syllabic** - True if the phoneme is syllabic

Lexicon
=======

.. code-block:: none

    idlak-data/<lng>/<acc>/lexicon-default.xml

*Accent specific*

The lexicon or pronounciation dictionary lists words that have known pronounciations
using the accent specific phoneset. It is possible to have multiple pronounciations for the
same word (grapheme). The lexicon format for a single entry is as follows:

.. code-block:: xml

    <lex pron="" entry="" default="">GRAPHEME</lex>

for example

.. code-block:: xml

    <lex pron="ih0 g z ae1 m p ah0 l" entry="full" default="true">example</lex>


Where

* **pron** - The correct pronounciation, including stress, using the Idlak phoneset.
* **entry** - A name for different pronounciations. Commonly these can be something like
              ``full``,  ``reduced``, ``noun``, or ``verb``. Alternatively these can
              be numbers to indicate multiple correct pronounciations. The allows for
              homograph resolution and  for the user to change which entry is spoken in
              the input.
* **default** - Which entry should be pronounced given no other information,
                one and only one entry must be true.

The overall format for the lexicon is:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <lexicon>
        <lex pron="a0" entry="full" default="true">а</lex>
        ..
    </lexicon>

The lexicon has an optional ``name`` attribute.


LTS rules
=========

.. code-block:: none

    idlak-data/<lng>/<acc>/ccart-default.xml

*Accent specific*

Currently the Idlak front-end uses cart trees for letter-to-sound rules.

*TODO: how to make cart trees from lexicon*



Tokeniser rules
===============

.. code-block:: none

    idlak-data/<lng>/trules-default.xml

Normalizer rules
================



Part of speech set and rules
============================



Abbreviations
=============



Phrasing rules
==============



Context extraction rules
========================




*******************
Available languages
*******************

* English
* Dutch
* Russian

