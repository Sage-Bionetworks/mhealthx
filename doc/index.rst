===================
Welcome to mhealthx
===================

`Sage Bionetworks`_ is developing mhealthx as an open source feature extraction pipeline
for mobile health research apps such as mPower_, the Parkinson disease symptom tracking app built on top of Apple's ResearchKit. See our software `documentation`_ and Github `repository`_ maintained by `Arno`_.

|

In particular, please see:

gait_ feature extraction from accelerometer data

tapping_ feature extraction from a touch screen tapping task

`main function`_ that calls all the feature extraction methods

|

----------

**References**

Arora S, Little MA, Venkataraman V, Donohue S, Biglan K, Dorsey ER. High-accuracy discrimination of Parkinson’s disease participants from healthy controls using smartphones. Movement Disorders 28(10):e12. 2013.

Bahrampoura S, Rayb A, Sarkarb S, Damarlac T, Nasrabadic NM. Performance comparison of feature extraction algorithms for target detection and classification. Pattern Recognition Letters 34(16):2126–2134. 2013. doi:10.1016/j.patrec.2013.06.021.

Eyben F, Weninger F, Gross F, Schuller B. Recent Developments in openSMILE, the Munich Open-Source Multimedia Feature Extractor. In Proc. ACM Multimedia (MM), Barcelona, Spain, ACM, ISBN 978-1-4503-2404-5:835-838. 2013. doi:10.1145/2502081.2502224.

Goetz CG, Stebbins GT, Wolff D, DeLeeuw W, Bronte-Stewart H, Elble R, Hallett M, Nutt J, Ramig L, Sanger T, Wu AD, Kraus PH, Blasucci LM, Shamim EA, Sethi KD, Spielman J, Kubota K, Grove AS, Dishman E, Taylor CB. Testing objective measures of motor impairment in early Parkinson's disease: Feasibility study of an at-home testing device. Mov Disord 24(4):551-6. 2009. doi:10.1002/mds.22379.

Yang M, Zheng H, Wang H, McClean S, Newell D. iGAIT: an interactive accelerometer based gait analysis system. Comput Methods Programs Biomed 108(2):715-23. 2012. doi:10.1016/j.cmpb.2012.04.004.


..
  .. raw:: html
  <div id='r' style='width:400px; height:300px; margin:20px; align:center; background-color:black'></div>

.. _`Sage Bionetworks`: http://sagebase.org
.. _mPower: http://parkinsonmpower.org
.. _documentation: http://sage-bionetworks.github.io/mhealthx/api/index.html
.. _repository: https://github.com/sage-bionetworks/mhealthx
.. _Arno: http://binarybottle.com
.. _gait: http://sage-bionetworks.github.io/mhealthx/api/generated/mhealthx.extractors.pyGait.html
.. _tapping: http://sage-bionetworks.github.io/mhealthx/api/generated/mhealthx.extractors.tapping.html
.. _`main function`: http://sage-bionetworks.github.io/mhealthx/api/generated/mhealthx.extract.html