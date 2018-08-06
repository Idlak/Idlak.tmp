#############
Tangle Voices
#############

Tangle is the name given to the IDLAK default voice building recipe.

**************************
Tangle system architecture
**************************

Documentation on what Tangle is here

Don't forget reference to paper

************************
Tangle voice file format
************************

First ensure there is the appropriate language resources in the correct locations.
See :ref:`language-resources`

* Language codes are 2 letter ISO_639-1 codes:  https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
* Accent codes are 2 ASCII letters
* Speaker codes are 3 ASCII letters.

Individual samples and files are of the form::

  <spk>_<g>nnnn_nnn[_nnn]

Where:

* **spk**  - a three letter lower case speaker name
* **g**    - a single lower case ASCII character which indicates a genre of utterances
* **nnnn** - a four digit number which can be used for paragraph or utterance set etc. (start at 0001)
* **nnn**  - a three digit utterance number (start at 000)
* for utterenaces that have been further split (i.e by extra pauses) an optional three digit 'part' number (start at 000)

Audio
=====

A speaker's audio files compressed (with tar) and uploaded to::

   idlak_resources/lng/acc/spk/lng.acc.spk.srate.tar.gz

Where ``srate`` is the sample rate in Herz.

For example the Russian audio is saved in ``idlak_resources/ru/ru/abr/ru.ru.abr.48000.tar.gz``

The audio files must match the IDs in the script and must have a ``.wav`` extension.

When decompressed the audio should be in a folder called ``srate_orig``

Script
======

A speaker specific script should be located in

idlak_resources/lng/acc/spk/text.xml

This will allow you to match the speaker's pronounciation by using SSML
to override the pronounciation of single words, or change words all together.

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

#. ID must match the audio files and all audio files must exist.
#. The xml declaration with encoding is manditory.





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

