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
PATH="/shared/software/bin:$PATH"

# Install essentia:
#./waf configure --mode=release --with-python --lightweight=libav
#./waf -> "cannot find -lavresample"

# Install mhealthx nipype workflow for feature extraction:
cd /shared/software
git clone git@github.com:binarybottle/mhealthx.git
cd /shared/software/mhealthx
python setup.py install
PATH="/shared/software/mhealthx/mhealthx:$PATH"