#!/bin/bash
# Takes a lexicon a generates letter-to-sound rules

set -eo pipefail

# Usage message
usage="Usage: "$0" -i <input lexicon>

  Optional flags and parameters:
    -h: show usage
    -o: output file
      default = ccart-default.xml
    -p: path to storage directory
      default = tmp

  The following Phonetisaurus arguments can be set as environment variables:
    delim: delimiter between lexicon attributes
      default = \" \"
    s2_char_delim: delimiter between phones
      default = \"_\"\n"

# Flag to detect if input directory has been set
iflag=false

# Some default values for parameters
output="ccart-default.xml"
phonet2cartpath="../../idlak-misc/cart_lts/"
cart2toolspath="../../tools"
storagedirectory="tmp"

# Argument handling
while getopts "i:o:hp:" opt
do
    case $opt in
        i)
            lexicon=$OPTARG
            iflag=true
            ;;
        o)
            output=$OPTARG
            ;;
        h)
            echo -e "$usage"
            exit 0
            ;;
        p)
            storagedirectory="$OPTARG"
            ;;
        \?)
            echo "Invalid option: -"$OPTARG"" >&2
            echo -e "$usage" >&2
            exit 1
            ;;
    esac
done

# Error if no input file
if ! $iflag
then
    echo "$usage" >&2
    exit 1
fi

# Check input file format
if [[ ${lexicon: -4} != ".lex" ]]
    then
        echo "Lexicon must be a .lex file"
        exit 1
fi

# Phonetisaurus enviornment variables
if [ ${#delim} -eq 0 ]
    then
        delim=" "
fi

if [ ${#s2_char_delim} -eq 0 ]
    then
        s2_char_delim="_"
fi

align="${lexicon::-4}"".align"
converted="converted.lex"

mkdir -p "$storagedirectory"

echo "#####Converting lexicon#####"
cat "$lexicon" | cut -d " " -f 1-2 > "$storagedirectory"/converted.lex

cd "$cart2toolspath"

echo "#####Installing Phonetisaurus#####"
if [ ! -d "Phonetisaurus" ]
then
    git clone https://github.com/AdolfVonKleist/Phonetisaurus.git
    cd Phonetisaurus
    git checkout 64719ca40c17cb70d810fffadac52c97984ca539 . || exit 1
    CXXFLAGS="-I`pwd`/../openfst/include" LDFLAGS="-Wl,-rpath=`pwd`/../openfst/lib/" \
    ./configure --with-openfst-libs=`pwd`/../openfst/lib \
        --with-openfst-includes=`pwd`/../openfst/include  \
        --prefix=`pwd`
    make -j4
    make install
else
    echo "Phonetisaurus already installed"
fi

echo "#####Creating alignment file#####"
cd Phonetisaurus
./phonetisaurus-align \
--input="$phonet2cartpath""$storagedirectory""/""$converted" \
--ofile="$phonet2cartpath""$storagedirectory""/""$align" \
--delim="$delim" \
--s2_char_delim="$s2_char_delim"
# Add more Phonetisaurus arguments here if needed
# Run ./phonetisaurus-align -help in idlak/tools/Phonetisaurus for more options

echo "#####Generating cart files#####"
cd "$phonet2cartpath""$storagedirectory"
pwd
python ../phonet2cart.py "$align"

echo "#####Running wagon#####"
for f in *.cart
do
    ID=${f::-5}
    mkdir -p cart/"$ID"
    wagon -desc wagon_description.dat -data "$f" -o cart/"$ID"/tree.dat
done

echo "#####Generating lts rules#####"
python ../carttree2xml.py cart "$output"
mv "$output" ..

echo "#####Done#####"
