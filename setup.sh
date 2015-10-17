# Installation of mhealthx and dependencies.
#
# by Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com
#
# Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

# Set bin path:
mkdir /shared/software/bin
PATH="/shared/software/bin:$PATH"

# Install Continuum's miniconda Python distribution and some Python libraries:
wget -nc http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -P /shared/software
chmod +x /shared/software/Miniconda-latest-Linux-x86_64.sh
bash /shared/software/Miniconda-latest-Linux-x86_64.sh -b -f -p /shared/software/anaconda
/shared/software/anaconda/bin/conda install --yes numpy scipy pandas nose networkx traits ipython # matplotlib

# Install nipype pipeline framework:
pip install nipype

# https://pythonhosted.org/lockfile/lockfile.html
pip install lockfile

# Install ffmpeg dependencies:
# (from https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu)
mkdir /shared/software/ffmpeg
mkdir /shared/software/ffmpeg/ffmpeg_sources
mkdir /shared/software/ffmpeg/ffmpeg_build
sudo apt-get update
sudo apt-get -y --force-yes install autoconf automake build-essential libass-dev libfreetype6-dev libsdl1.2-dev libtheora-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev libxcb-xfixes0-dev pkg-config texi2html zlib1g-dev

# Install yasm (ffmpeg dependency):
cd /shared/software/ffmpeg/ffmpeg_sources
wget -nc http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz
tar xzvf yasm-1.3.0.tar.gz
cd /shared/software/ffmpeg/ffmpeg_sources/yasm-1.3.0
./configure --prefix="/shared/software/ffmpeg/ffmpeg_build" --bindir="/shared/software/bin"
make
make install
make distclean

# Install ffmpeg:
cd /shared/software/ffmpeg/ffmpeg_sources
wget -nc http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg
PATH="/shared/software/bin:$PATH" PKG_CONFIG_PATH="/shared/software/ffmpeg/ffmpeg_build/lib/pkgconfig" ./configure --prefix="/home/shared/software/ffmpeg/ffmpeg_build" --pkg-config-flags="--static" --extra-cflags="-I/home/shared/software/ffmpeg/ffmpeg_build/include" --extra-ldflags="-L/home/shared/software/ffmpeg/ffmpeg_build/lib" --bindir="/home/shared/software/bin" --enable-gpl
#--enable-libass --enable-libfreetype --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libx265 --enable-nonfree --enable-libfdk-aac --enable-libmp3lame --enable-libopus --enable-libvpx
make
make install
PATH="/shared/software/ffmpeg/ffmpeg_sources/ffmpeg:$PATH"

# Install openSMILE:
cd /shared/software
wget -nc http://binarybottle.com/software/openSMILE-2.1.0.tar.gz
tar xvf openSMILE-2.1.0.tar.gz
cd openSMILE-2.1.0
bash buildStandalone.sh -p /shared/software
#PATH="/shared/software/bin:$PATH"

# Install Essentia dependencies:
sudo apt-get install libyaml-dev libfftw3-dev libavcodec-dev libavformat-dev libavutil-dev libavresample-dev python-dev libsamplerate0-dev libtag1-dev
#    build-essential
sudo apt-get install pkg-config
pip install pyyaml

# Install Essentia:
#cd /shared/software
##git clone https://github.com/MTG/essentia.git
##cd essentia
#wget -nc https://github.com/MTG/essentia/archive/v2.1_beta2.tar.gz
#tar xvf essentia-v2.1_beta2.tar.gz
#cd essentia-v2.1_beta2
#./waf configure --mode=release --with-python --with-cpptests --with-examples
#./waf
##sudo mkdir /usr/local/include/essentia
##sudo mkdir /usr/local/include/essentia/scheduler
##chmod 777 src
##chmod 777 src/version.h
##chmod 777 src/algorithms
##chmod 777 src/algorithms/essentia_algorithms_reg.cpp
##./waf build
#sudo ./waf install

# Install Kaldi dependencies:
sudo apt-get install libtool subversion
sudo apt-get install libatlas-dev libatlas-base-dev

# Install Kaldi:
cd /shared/software
git clone https://github.com/kaldi-asr/kaldi.git kaldi-trunk --origin golden
cd /shared/software/kaldi-trunk/tools
make
cd /shared/software/kaldi-trunk/src
./configure; make depend; make

# Install YAAFE dependencies:
#sudo apt-get install cmake-curses-gui libargtable2-0 libargtable2-dev libsndfile1 libsndfile1-dev libmpg123-0 libmpg123-dev libfftw3-3 libfftw3-dev liblapack-dev libhdf5-serial-dev libhdf5-7
##   cmake
# Install YAAFE:
#mkdir build; cd build
#ccmake -DCMAKE_PREFIX_PATH=/shared/software/yaafe-v0.64/build/lib -DCMAKE_INSTALL_PREFIX=/shared/software/yaafe-v0.64/ ..
#make; make install

# Install jAudio dependencies:
#sudo apt-get install ant
#sudo apt-get install openjdk-7-jdk
# Install jAudio:
#git clone https://github.com/anjackson/jAudio.git
#cd /shared/software/jAudio
#ant jar
#...

# Install grt:
#sudo apt-get install g++-4.8

# Install text to audio conversion:
pip install scikit-learn

# Install mhealthx nipype workflow for feature extraction:
cd /shared/software
git clone git@github.com:binarybottle/mhealthx.git
cd /shared/software/mhealthx
python setup.py install
PATH="/shared/software/mhealthx/mhealthx:$PATH"