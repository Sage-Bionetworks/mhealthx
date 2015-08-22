==============================================================================
README for Sage Bionetwork's mHealth feature extraction software pipeline
==============================================================================
| 1. `Introduction and help`_
| 2. `Input`_
| 3. `Processing steps`_
| 4. `Output`_

------------------------------------------------------------------------------
_`Introduction and help`
------------------------------------------------------------------------------
This open source (Nipype) pipeline automates feature extraction 
from mobile health data saved to synapse.org.

- For help in a terminal window::

    extractor -h

- `GitHub <http://github.com/binarybottle/voice-feature-extractor>`_
- `License <http://www.apache.org/licenses/LICENSE-2.0>`_

------------------------------------------------------------------------------
_`Input`
------------------------------------------------------------------------------
The mPower app's voice files are stored in m4a (aac) format in a synapse.org project.

------------------------------------------------------------------------------
_`Processing steps`
------------------------------------------------------------------------------
Processing: 

  - Pull m4a (aac) voice files from mPower app's synapse.org project.
  - Convert each voice file from m4a to wav format.
  - Run different voice feature extraction software packages on the wav files.
  - Output features to a new synapse.org table.

------------------------------------------------------------------------------
_`Output`
------------------------------------------------------------------------------
Output:

  - wav files
  - Synapse Tables