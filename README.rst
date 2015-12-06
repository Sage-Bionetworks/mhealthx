==============================================================================
README for Sage Bionetwork's mhealthx feature extraction software pipeline
==============================================================================
| 1. `Introduction`_
| 2. `Inputs`_
| 3. `Processing`_
| 4. `Outputs`_

------------------------------------------------------------------------------
_`Introduction`
------------------------------------------------------------------------------
This open source software pipeline automates feature extraction 
from mobile health data saved as a Synapse project (synapse.org).

  - For help in a terminal window:  mhealthx -h
  - `GitHub repository <https://github.com/Sage-Bionetworks/mhealthx>`_
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
  - Output features to new tables.

------------------------------------------------------------------------------
_`Outputs`
------------------------------------------------------------------------------
  - Tables
