==============================================================================
README for Sage Bionetwork's mHealth feature extraction software pipeline
==============================================================================
| 1. `Introduction`_
| 2. `Inputs`_
| 3. `Preprocessing`_
| 4. `Processing`_
| 5. `Outputs`_

------------------------------------------------------------------------------
_`Introduction`
------------------------------------------------------------------------------
This open source (Nipype) pipeline automates feature extraction 
from mobile health data saved as a Synapse project (synapse.org).

  - For help in a terminal window:  extractor -h
  - `GitHub repository <http://github.com/binarybottle/voice-feature-extractor>`_
  - `Apache v2.0 license <http://www.apache.org/licenses/LICENSE-2.0>`_

------------------------------------------------------------------------------
_`Inputs`
------------------------------------------------------------------------------
All data are accessed from Synapse tables in a project on synapse.org:

  - Voice: WAV files
  - Tapping: JSON files
  - Accelerometry: JSON files

------------------------------------------------------------------------------
_`Processing`
------------------------------------------------------------------------------
  - Run different feature extraction software packages on the input data.
  - Output features to new tables on synapse.org.

------------------------------------------------------------------------------
_`Outputs`
------------------------------------------------------------------------------
  - Synapse tables
