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

  - Accelerometry: JSON files
  - Tapping: JSON files
  - Voice: M4A (AAC) files

------------------------------------------------------------------------------
_`Preprocessing`
------------------------------------------------------------------------------
Voice data:

  - Pull M4A voice files from synapse.org.
  - Convert M4A files to WAV format.
  - Store fileIDs for preprocessed data to new tables on synapse.org.

------------------------------------------------------------------------------
_`Processing`
------------------------------------------------------------------------------
  - Run different feature extraction software packages on the (preprocessed) inputs.
  - Output features to new tables on synapse.org.

------------------------------------------------------------------------------
_`Outputs`
------------------------------------------------------------------------------
  - Synapse tables
  - Under consideration: fileIDs for intermediate processed results?