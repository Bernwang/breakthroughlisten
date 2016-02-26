The current system at GBT is a high speed data recorder, recording voltages as a function of time - the lowest level product you can get from a radio telescope. We also want to build higher level products, in particular, spectral (detected) data. The link between them is a fast Fourier transform, and then a power computation.

The bandwith (frequency range) we can sample depends on how fast we can sample the voltages. For example, 100 million samples per second implies 50 MHz bandwidth (via the Nyquist criterion). The analog signal from the telescope goes into a digitizer (iADC / iBOB), and then into the SETI processor, which divides the signal up into individual frequency channels, computes the power, and performs a thresholding operation.

The VEGAS instrument at GBT is a big digitizer. It samples at 20 gigasamples / s which gives 10 GHz usable bandwidth. Right now we only run one of VEGAS’s eight ROACH boards, so we get 1/8 of the total bandwidth (about 1.25 GHz). These data come over 10 gigabit ethernet through a network switch to the BL compute infrastructure.Breakthrough Listen will eventually duplicate the existing compute infrastructure by a factor 8, allowing the whole 10 GHz bandwidth to be recorded.

Coarse channelization (using a polyphase filter bank, essentially a big bank of bandpass filters) breaks the incoming band into 256 or 512 pieces.

The Breakthrough machines consist of the head node, storage notes, and compute nodes:

Head node: Contains boot images for the other systems in the cluster.
Storage node (currently 1, will be 8): Long term archival storage with RAID6.
Compute / high speed storage mode (currently 8, will be 64): Where the action happens when we are doing observations. They record raw data to disk. All of the analysis will happen here, in place.

GUPPI (Green bank Ultimate Pulsar Machine) is the old pulsar machine at GBT, that was used for the first SETI observations there. It’s only 800 MHz bandwidth, but it’s the only instrument there currently that can do pulsar timing and has a well-tested baseband capability (i.e. the ability to write raw voltages). The GUPPI software (somewhat modified by Breakthrough engineer Dave MacMahon) is what’s used to record BL data on our new machines.

To generate the high level data products, we take as input a coarsely channelized voltage as a function of time. Output is power as a function of time and frequency, aslo referred to as a waterfall plot. For now let's just look at total intensity (Stokes I), rather than considering the polarization data.

The raw voltages are stored in GUPPI-raw format (also called PSRFITS-raw or “baseband data”).

Compared to the information about SETI Brainstorm. Information about the file format is at the SETI Brainstorm page at https://seti.berkeley.edu/GBT_SETI_Data_Description . For BL data, the channel ordering is flipped in frequency, and the files are written natively as 8 bit rather than 2 bit (although we're requantizing much of the data to 2 bit after it's taken).

The output from the BL switch is 8 chunks of 64 channels of ~3 MHz width (⅛ of the Nyquist band). Each compute node gets a consecutive chunk in frequency.

Files are stored as one sequence of files per observation per node. There are 64 voltage streams per file. Each file in a sequence is about 18 GB, corresponding to about 20 seconds in time.

There are tools on the compute nodes that allow us to generate waterfall plots from the raw voltage files. The output format is “filterbank” (filenames ending in .fil). These have a header that is about 250 bytes, and then a bunch of spectral data, in a sequence of total power spectra from zero up to N.

There are currently four principal code bases. Two pulsar code bases, the GBT spectral line and continuum data reduction code (mostly in IDL), and GBT SETI (there's a github repository for this), which contains the rudiments of the pipeline that we run at GBT. 

We would like to set up a virtual machine to run the pulsar code, although for now it's also installed on the machines at GBT. 

The tools are
sigproc
DSPSR
PSRchive
Tempo 1 & 2
PSRDADA
[the above are installed with PSRSOFT]
and Presto

If you have an account, do successively:
ssh user@ssh.gb.nrao.edu
ssh user@bl-head
ssh user@blc5

All machines are net booted, and each has drives /datax (XFS formatted) and /data (ext4 formatted). These are planned to switch to JBOD at some point.

cd /datax (where the files are written when we are running an observation). Files are written into a folder called dibas. When the observing is done, Matt does data massaging to get things into the canonical GUPPI-raw format. Don’t play around in here while observations are in progress - the system needs all of the I/O.

Run the data reduction on the storage node, so 
ssh user@bls0
cd /datax/blc3/dibas.20160109/AGBT16A_999_17_GUPPI/D [example directory]

fold -w 80 * | more

cd /usr/local/pulsar64
source pulsar.bash
cd ../sigproc/bin
source sigproc.sh

The first tool we’ll use is DSPSR - a preprocessor for pulsar observations. It’s a toolbox for voltage data. The program digistat takes in raw files and produces a plot of polyphase channels.

digistat blc3_guppi_57396_MESSIER031_0040.0000.raw -s 0.05

(use graphics device /XWIN - or you can write to a /PNG etc.)

Let’s plot a passband:

passband blc3_guppi_57396_MESSIER031_0040.0000.raw -b -n 512 -t 0.05

The comb of delta functions are the DC channels for each of the polyphase channels. Green and red are the two polarizations.

digihist - prints samples to stdout

digifil - produces filterbank output (waterfall plot). Can run this on a sequence of files.

digifil blc3_guppi_57396_MESSIER031_0040.* -b -32 -F 2048:D -t 1024 -I 0 -o test.fil

-b -32 gives 32-bit floats
-F 2048 gives 2048 channels
Only the polyphase filter bank is set up to deal with multi-channel data, so you have to use the :D at the end of the -F specifier.
-t 1024 sums total power every 1000 spectra (collapsing in time)

By default, digifil zaps birdies. We need to be careful about this, since a signal from ET might look like a birdie, so use -I 0 to set the rescale interval to zero.

Digifil will probably take 5 minutes or so to produce the output file.

Once we have the output, we can check the header, like

header test.fil

You can plot the .fil file using your favorite plotting program (e.g. chop off the header and read the rest in as a binary blob), or you can use some of the sigproc tools to interact with it. For example, if you want to see power as a function of frequency, you can do
bandpass test.fil
For developing this going forward, we need to develop a GPU-accelerated pipeline.
