## launch an instance of the starcluster base image: 
## starcluster-base-ubuntu-12.04-x86_64 - ami-765b3e1f
## see: http://star.mit.edu/cluster/


sudo apt-get update

sudo apt-get install -y git
	
# Install Continuum's miniconda Python distribution and some Python libraries:
wget -nc http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
chmod +x Miniconda-latest-Linux-x86_64.sh
# -b           run install in batch mode (without manual intervention),
#              it is expected the license terms are agreed upon
# -f           no error if install prefix already exists
# -p PREFIX    install prefix, defaults to /home/ubuntu/miniconda
bash ./Miniconda-latest-Linux-x86_64.sh -b -f
PATH="/home/ubuntu/miniconda/bin":$PATH
conda install --yes numpy scipy pandas nose networkx traits ipython matplotlib

# Install nipype pipeline framework:
/home/ubuntu/miniconda/bin/pip install nipype
/home/ubuntu/miniconda/bin/pip install synapseclient

# Install ffmpeg dependencies
sudo apt-get install -y autoconf automake build-essential libass-dev libfreetype6-dev libsdl1.2-dev libtheora-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev libxcb-xfixes0-dev pkg-config texi2html zlib1g-dev

mkdir /home/ubuntu/ffmpeg
mkdir /home/ubuntu/ffmpeg/ffmpeg_sources
mkdir /home/ubuntu/ffmpeg/ffmpeg_build

cd /home/ubuntu/ffmpeg/ffmpeg_sources
wget -nc http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz
tar xzvf yasm-1.3.0.tar.gz
cd /home/ubuntu/ffmpeg/ffmpeg_sources/yasm-1.3.0
./configure --prefix="/home/ubuntu/ffmpeg/ffmpeg_build" --bindir="/home/ubuntu/bin"
make
make install
make distclean

# Install ffmpeg:
cd /home/ubuntu/ffmpeg/ffmpeg_sources
wget -nc http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg
PATH="/home/ubuntu/bin:$PATH" PKG_CONFIG_PATH="/home/ubuntu/ffmpeg/ffmpeg_build/lib/pkgconfig" ./configure --prefix="/home/ubuntu/ffmpeg/ffmpeg_build" --pkg-config-flags="--static" --extra-cflags="-I/home/ubuntu/ffmpeg/ffmpeg_build/include" --extra-ldflags="-L/home/ubuntu/ffmpeg/ffmpeg_build/lib" --bindir="/home/ubuntu/bin" --enable-gpl
#--enable-libass --enable-libfreetype --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libx265 --enable-nonfree --enable-libfdk-aac --enable-libmp3lame --enable-libopus --enable-libvpx
make
make install
PATH="/home/ubuntu/ffmpeg/ffmpeg_sources/ffmpeg:$PATH"

# Install openSMILE:
cd /home/ubuntu
wget -nc http://binarybottle.com/software/openSMILE-2.1.0.tar.gz
tar xvf openSMILE-2.1.0.tar.gz
cd openSMILE-2.1.0
bash buildStandalone.sh -p /home/ubuntu
PATH="/home/ubuntu/bin:$PATH"

# Install mhealthx nipype workflow for feature extraction:
# cd /home/ubuntu
# git clone https://github.com/binarybottle/mhealthx.git
# cd /home/ubuntu/mhealthx
# python setup.py install
# PATH="/home/ubuntu/mhealthx/mhealthx:$PATH"

