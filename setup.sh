#!/bin/bash
#=============================================================================
# This script provides directions for installing mhealthx and dependencies
# (http://sage-bionetworks.github.io/mhealthx/).
# Running it requires a good Internet connection.
# Tested on an Ubuntu 14.04 machine.
#
# Usage:
#     bash setup.sh 1
#
#     bash setup.sh <install_mhealthx> <install_dir>
#       <install_mhealthx>: 1 or 0 (do/not install mhealthx)
#       <install_dir>: path to installation directory (optional)
#
# Note:
#     Third-party software not in the GitHub repository are on Synapse:
#     https://www.synapse.org/#!Synapse:syn5584792
#
# Authors:
#     - Arno Klein, 2015-2016  (arno@sagebase.org)  http://binarybottle.com
#
# Copyright 2016,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License
#=============================================================================

#-----------------------------------------------------------------------------
# Assign download and installation path.
# Create installation folder if it doesn't exist:
#-----------------------------------------------------------------------------
MHEALTHX=$1
INSTALLS=$2
if [ -z $MHEALTHX ]; then
    MHEALTHX=1
fi
if [ -z $INSTALLS ]; then
    INSTALLS=$HOME/install
fi
if [ ! -d $INSTALLS ]; then
    mkdir -p $INSTALLS;
fi
export INSTALLS
export PATH=$INSTALLS/bin:$PATH

#-----------------------------------------------------------------------------
# System-wide dependencies:
#-----------------------------------------------------------------------------
sudo apt-get update
sudo apt-get install -y git
sudo apt-get install -y build-essential

#-----------------------------------------------------------------------------
# Anaconda's miniconda Python distribution for local installs:
#-----------------------------------------------------------------------------
CONDA_URL="http://repo.continuum.io/miniconda"
CONDA_FILE="Miniconda-latest-Linux-x86_64.sh"
CONDA_DL=$INSTALLS/${CONDA_FILE}
CONDA_PATH=$INSTALLS/miniconda2
CONDA=${CONDA_PATH}/bin
wget -O $CONDA_DL ${CONDA_URL}/$CONDA_FILE
chmod +x $CONDA_DL
# -b           run install in batch mode (without manual intervention),
#              it is expected the license terms are agreed upon
# -f           no error if install prefix already exists
# -p PREFIX    install prefix
bash $CONDA_DL -b -f -p $CONDA_PATH
export PATH=$CONDA:$PATH

#-----------------------------------------------------------------------------
# Additional resources for installing packages:
#-----------------------------------------------------------------------------
$CONDA/conda install --yes cmake pip

#-----------------------------------------------------------------------------
# Install some Python libraries:
#-----------------------------------------------------------------------------
$CONDA/conda install --yes numpy scipy pandas nose networkx traits ipython matplotlib

# Install nipype pipeline framework:
$CONDA/pip install nipype

# Install Synapse client:
$CONDA/pip install synapseclient

# https://pythonhosted.org/lockfile/lockfile.html
$CONDA/pip install lockfile

# Install scikit-learn for text-to-audio conversion:
$CONDA/pip install scikit-learn

#-----------------------------------------------------------------------------
# Install mhealthx nipype workflow for feature extraction:
#-----------------------------------------------------------------------------
if [ "$MHEALTHX" -eq "1" ]; then
    cd $INSTALLS
    git clone git@github.com:sage-bionetworks/mhealthx.git
    cd $INSTALLS/mhealthx
    sudo python setup.py install
    export PATH=$INSTALLS/mhealthx/mhealthx:$PATH
    export PYTHONPATH=$PYTHONPATH:$INSTALLS/mhealthx
fi

#-----------------------------------------------------------------------------
# Install ffmpeg and dependencies for audio file conversion:
#-----------------------------------------------------------------------------
# (from https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu)
mkdir $INSTALLS/ffmpeg
mkdir $INSTALLS/ffmpeg/ffmpeg_sources
mkdir $INSTALLS/ffmpeg/ffmpeg_build
sudo apt-get -y --force-yes install autoconf automake build-essential libass-dev libfreetype6-dev libsdl1.2-dev libtheora-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev libxcb-xfixes0-dev pkg-config texi2html zlib1g-dev

# Install yasm (ffmpeg dependency):
cd $INSTALLS/ffmpeg/ffmpeg_sources
wget -nc http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz
tar xzvf yasm-1.3.0.tar.gz
cd $INSTALLS/ffmpeg/ffmpeg_sources/yasm-1.3.0
./configure --prefix="$INSTALLS/ffmpeg/ffmpeg_build" --bindir="$INSTALLS/bin"
make
make install
make distclean

# Install ffmpeg:
cd $INSTALLS/ffmpeg/ffmpeg_sources
wget -nc http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg
PKG_CONFIG_PATH=$INSTALLS/ffmpeg/ffmpeg_build/lib/pkgconfig
./configure --prefix=$INSTALLS/ffmpeg/ffmpeg_build --pkg-config-flags="--static" --extra-cflags="-I$INSTALLS/ffmpeg/ffmpeg_build/include" --extra-ldflags="-L$INSTALLS/ffmpeg/ffmpeg_build/lib" --bindir="$INSTALLS/bin" --enable-gpl
#--enable-libass --enable-libfreetype --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libx265 --enable-nonfree --enable-libfdk-aac --enable-libmp3lame --enable-libopus --enable-libvpx
make
make install
export PATH=$INSTALLS/ffmpeg/ffmpeg_sources/ffmpeg:$PATH

#-----------------------------------------------------------------------------
# Install openSMILE:
#-----------------------------------------------------------------------------
cd $INSTALLS
synapse get syn5584794
tar xvf openSMILE-2.1.0.tar.gz
cd openSMILE-2.1.0
bash buildStandalone.sh -p $INSTALLS

#-----------------------------------------------------------------------------
# Other voice feature extraction software (for future integration):
#-----------------------------------------------------------------------------
# Install Essentia dependencies:
#sudo apt-get install libyaml-dev libfftw3-dev libavcodec-dev libavformat-dev libavutil-dev libavresample-dev python-dev libsamplerate0-dev libtag1-dev
#    build-essential
#sudo apt-get install pkg-config
#$CONDA/pip install pyyaml

# Install Essentia:
#cd $INSTALLS
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
#sudo apt-get install libtool subversion
#sudo apt-get install libatlas-dev libatlas-base-dev

# Install Kaldi:
#cd $INSTALLS
#git clone https://github.com/kaldi-asr/kaldi.git kaldi-trunk --origin golden
#cd $INSTALLS/kaldi-trunk/tools
#make
#cd $INSTALLS/kaldi-trunk/src
#./configure; make depend; make

# Install YAAFE dependencies:
#sudo apt-get install cmake-curses-gui libargtable2-0 libargtable2-dev libsndfile1 libsndfile1-dev libmpg123-0 libmpg123-dev libfftw3-3 libfftw3-dev liblapack-dev libhdf5-serial-dev libhdf5-7
##   cmake
# Install YAAFE:
#mkdir build; cd build
#ccmake -DCMAKE_PREFIX_PATH=$INSTALLS/yaafe-v0.64/build/lib -DCMAKE_INSTALLS=$INSTALLS/yaafe-v0.64/ ..
#make; make install

# Install jAudio dependencies:
#sudo apt-get install ant
#sudo apt-get install openjdk-7-jdk
# Install jAudio:
#git clone https://github.com/anjackson/jAudio.git
#cd $INSTALLS/jAudio
#ant jar
#...

# Install grt:
#sudo apt-get install g++-4.8
