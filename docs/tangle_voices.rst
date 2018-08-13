#############
Tangle Voices
#############

Tangle is the name given to the IDLAK default voice building recipe. Above all
Tangle is meant to work out of the box and be easy to add voices and languages to.

**************************
Tangle system architecture
**************************

Tangle is a DNN based synthesiser. It is intended as a baseline system for your
own research, as such it was designed to be straight-forward to understand
and easy to use, rather than neccessarly producing the highest possible quality.
The details of the system are explained in the paper below here we are only giving,
a high level overview.

The tangle scripts in the idlak-egs directory are responsible for training models
for voices using different data sources. A location independant voice directory
is created once the script is finished. Briefly the process is as follows:
Numbering matches the steps in the run.sh for the Idlak examples.

0. Download the audio and text data and prepares the inputs for training.
1. Decomposes the speech using a vocoder (currently using the Idlak / Kaldi mcep vocoder)
2. Uses the Idlak front-end to normalise the text and add context labels, including duration.
3. Uses Kaldi to do forced alignment.
4. Trains the DNN models for duration, f0, and vocoder features.
5. Packages the voice into a directory that contains all files required for synthesis.
6. Synthesizes the text in testdata.

There are some tools for synthesing using the Tangle voices. Firstly there is a command
line program (instructions are given once the script has finished running) and then
there is a RESTful server, see :ref:`rest-server`.

If you are using Tangle in your research please reference the following paper::

    Idlak Tangle: An Open Source Kaldi Based Parametric Speech Synthesiser Based on DNN.
        By Potard, Blaise and Aylett, Matthew P and Braude, David A and Motlicek, Petr

    Bibtex entry:

    @inproceedings{potard2016idlak,
        title={Idlak Tangle: An Open Source Kaldi Based Parametric Speech Synthesiser Based on DNN.},
        author={Potard, Blaise and Aylett, Matthew P and Braude, David A and Motlicek, Petr},
        booktitle={INTERSPEECH},
        year={2016},
        pages={2293-2297}
    }


************************
Tangle voice file format
************************

First ensure there is the appropriate language resources in the correct locations.
See :ref:`language-resources`

* Language (lng) codes are `2 letter ISO_639-1 codes <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_
* Accent (acc) codes are 2 ASCII letters, see :ref:`accents`
* Speaker (spk) codes are 3 ASCII letters.

Individual samples and files are of the form::

  <spk>_<g>nnnn_nnn[_nnn]

Where:

* **spk**  - a three letter lower case speaker code
* **g**    - a single lower case ASCII character which indicates a genre of utterances
* **nnnn** - a four digit number which can be used for paragraph or utterance set etc. (start at 0001)
* **nnn**  - a three digit utterance number (start at 000)
* for utterenaces that have been further split (i.e by extra pauses) an optional three digit 'part' number (start at 000)

Audio
=====

A speaker's audio files compressed (with tar) in a file called::

   <lng>.<acc>.<spk>.<srate>.tar.gz

Where ``srate`` is the sample rate in Herz.

For example the Russian audio is saved in ``ru.ru.abr.48000.tar.gz``

The audio files must match the IDs in the script and must have a ``.wav`` extension.

When decompressed the audio should be in a folder called ``<srate>_orig``

Currently Idlak audio is hosted at https://archive.org/ , however, any
other hosting service would be fine, as long as the example script is
able to run. A file containting only the URL for the audio is then added to::

    idlak_resources/<lng>/<acc>/<spk>/audiourl



Recording Script
================

For some languages a recording script is available at::

    idlak_resources/<lng>/<acc>/text.xml

A speaker specific script should be located in::

    idlak_resources/<lng>/<acc>/<spk>/text.xml

This will allow you to match the speaker's pronounciation by using SSML
to override the pronounciation of single words, or change words all together compared
to the original recording script. If you have developed a recording script
for a lanugage that does not have one then it can be added, but the speaker
code should be removed from the fileid name (see format below).

The general format of the recording script is as follows:

.. code-block:: xml

  <?xml version="1.0"? encoding="utf-8">
  <recording_script>
      <fileid id='name'>
          Text or SSML
      </fileid>
      ...
  </recording_script>

Note:

#. ID must match the audio files
#. Not all utterances need audio files, if the audio is missing it is ignored.
#. The xml declaration with encoding is manditory.
#. For consistancy please use utf-8 encoding


Final Steps
===========

The last few things to finish up:

#. Add some test data in utf-8 encoded xml format to ``idlak-data/<lng>/testdata`` directory
#. Add a sample sentence to the end of ``idlak-egs/tts_tangle_idlak/run.sh``


**************************
Notes on specific examples
**************************

Arctic voices
=============

Arctic have the form ``arctic_a0nnn`` and ``arctic_b0nnn`` which are remapped to ``bdl_a0001_nnn`` and ``bdl_b0001_nnn``

# audio is 16khz and copied to wavdir/16000_orig In general all original corpus audio
# should be copied to such a directory name reflecting sample rate etc.
# a symbolic link is then made between this directory and wavdir/16000 which is always
# the true input to the kaldi voice build system. If audio preprocessing is carried out
# then remove this link and create copies as appropriate.

